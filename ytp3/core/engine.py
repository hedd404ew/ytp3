"""Core download engine for YTP3Downloader."""

import time
import random
import traceback
import logging
import re
from io import StringIO
from .strategies import DownloadStrategy

try:
    import yt_dlp
except ImportError:
    raise ImportError("yt-dlp is required. Install with: pip install yt-dlp")


class YTP3Engine:
    """Main download engine handling metadata resolution and downloads."""
    
    # Format fallback hierarchy (5-layer degradation strategy)
    FORMAT_FALLBACKS = {
        'best': [
            ('bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', 'Best quality with merged audio'),
            ('bestvideo+bestaudio/best', 'Auto-select best video+audio'),
            ('bestvideo[height<=1080]+bestaudio/best', 'Best quality up to 1080p'),
            ('best[ext=mp4]', 'Single best MP4 format'),
            ('best', 'Fallback to absolute best available'),
        ],
        'high': [
            ('(bestvideo[height<=1080][ext=mp4]/best[height<=1080][ext=mp4])+(bestaudio[ext=m4a]/best)', '1080p with merged audio'),
            ('(bestvideo[height<=1080]/best[height<=1080])+bestaudio/best', '1080p video+audio'),
            ('best[height<=1080][ext=mp4]', 'Best 1080p MP4'),
            ('best[height<=720]', 'Fallback to 720p'),
            ('best', 'Fallback to best available'),
        ],
        'medium': [
            ('(bestvideo[height<=720][ext=mp4]/best[height<=720][ext=mp4])+(bestaudio[ext=m4a]/best)', '720p with merged audio'),
            ('(bestvideo[height<=720]/best[height<=720])+bestaudio/best', '720p video+audio'),
            ('best[height<=720][ext=mp4]', 'Best 720p MP4'),
            ('best[height<=480]', 'Fallback to 480p'),
            ('best', 'Fallback to best available'),
        ],
        'low': [
            ('(bestvideo[height<=480][ext=mp4]/best[height<=480][ext=mp4])+(bestaudio[ext=m4a]/best)', '480p with merged audio'),
            ('(bestvideo[height<=480]/best[height<=480])+bestaudio/best', '480p video+audio'),
            ('best[height<=480][ext=mp4]', 'Best 480p MP4'),
            ('worst[ext=mp4]', 'Worst quality MP4'),
            ('best', 'Fallback to best available'),
        ]
    }
    
    def __init__(self, options, capabilities, log_callback=None):
        """
        Initialize the download engine.
        
        Args:
            options (dict): yt-dlp download options
            capabilities (dict): System capabilities report
            log_callback (callable, optional): Callback function for logging
        """
        self.opts = options
        self.caps = capabilities
        self.log_cb = log_callback
        self.strategies = DownloadStrategy.get_all()
        self.last_detailed_error = ""

    def log(self, msg):
        """Log a message using callback or print."""
        if self.log_cb:
            self.log_cb(msg)
        else:
            print(msg)

    def resolve_metadata(self, url):
        """
        Resolve video/playlist metadata with fallback strategies.
        
        Args:
            url (str): YouTube URL to analyze
            
        Returns:
            list: List of video information dictionaries
            
        Raises:
            Exception: If metadata cannot be resolved after all strategies
        """
        last_error = ""
        
        for strategy in self.strategies:
            p_opts = {
                'quiet': True,
                'ignoreerrors': True,
                'extract_flat': 'in_playlist',
                'logger': None
            }
            
            # Preserve authentication options
            if 'cookiesfrombrowser' in self.opts:
                p_opts['cookiesfrombrowser'] = self.opts['cookiesfrombrowser']
            if 'cookiefile' in self.opts:
                p_opts['cookiefile'] = self.opts['cookiefile']
            
            p_opts.update(strategy['extra'])

            try:
                with yt_dlp.YoutubeDL(p_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    results = []
                    
                    # Handle playlists
                    if 'entries' in info:
                        for entry in info['entries']:
                            if entry:
                                results.append(entry)
                    else:
                        results.append(info)
                    
                    if results:
                        self.log(f"[METADATA] Resolved {len(results)} item(s) using {strategy['name']} strategy")
                        return results
                        
            except Exception as e:
                error_msg = str(e)
                
                # Handle cookie format errors
                if "Netscape format" in error_msg:
                    raise Exception("Invalid Cookie File. Must be Netscape format (not JSON).")
                
                last_error = error_msg
                self.log(f"[DEBUG] Metadata fetch with {strategy['name']}: {error_msg[:100]}")
                
                # Retry on signature/availability errors
                if "Signatures" in error_msg or "not available" in error_msg:
                    self.log(f"[RETRY] Trying next strategy...")
                    continue
                else:
                    break
        
        msg = f"Metadata fetch failed after all attempts: {last_error}"
        self.last_detailed_error = msg
        raise Exception(msg)

    def download_single_item(self, url, progress_callback=None):
        """
        Download a single video with 5-layer degradation fallback.
        
        Args:
            url (str): Video URL to download
            progress_callback (callable, optional): Callback for progress updates
            
        Raises:
            Exception: If download fails after all strategies and formats
        """
        success = False
        last_error = ""
        attempt_count = 0
        max_attempts = 20  # 5 strategies × 4 fallback formats
        
        # Random delay to avoid rate limiting
        time.sleep(random.uniform(0.5, 2.0))
        
        # Determine quality level
        quality = self.opts.get('format_quality', 'best')
        fallback_formats = self.FORMAT_FALLBACKS.get(quality, self.FORMAT_FALLBACKS['best'])
        
        self.log(f"[DOWNLOAD] Starting download with quality: {quality}")
        self.log(f"[FORMAT] Available fallback formats: {len(fallback_formats)}")

        for strategy in self.strategies:
            if success:
                break
            
            self.log(f"[STRATEGY] Attempting with {strategy['name']} bypass...")
            
            # Layer 1-5: Try each format fallback with this strategy
            for fallback_idx, (fmt, fmt_desc) in enumerate(fallback_formats, 1):
                if success:
                    break
                
                attempt_count += 1
                self.log(f"[ATTEMPT {attempt_count}] L{fallback_idx}: {fmt_desc}")
                
                try:
                    current_opts = self.opts.copy()
                    current_opts.update(strategy['extra'])
                    
                    # Critical merge settings
                    current_opts['format'] = fmt
                    current_opts['prefer_ffmpeg'] = True
                    current_opts['postprocessor_args'] = ['-c:v', 'copy', '-c:a', 'aac', '-loglevel', 'verbose']
                    
                    # Rate-limiting
                    current_opts['sleep_interval'] = random.randint(2, 5)
                    current_opts['max_sleep_interval'] = 10
                    
                    # Silence warnings but keep errors
                    current_opts['quiet'] = False
                    current_opts['no_warnings'] = False
                    
                    # Progress callback handler
                    def progress_hook(d):
                        if d['status'] == 'downloading' and progress_callback:
                            p = d.get('_percent_str', '0%').replace('%', '')
                            try:
                                # Strip ANSI color codes (\x1b[...m) from progress string
                                p_clean = re.sub(r'\x1b\[[0-9;]*m', '', p).strip()
                                pct = float(p_clean)
                                speed = d.get('_speed_str', 'N/A')
                                eta = d.get('_eta_str', '?')
                                size = d.get('_total_bytes_str') or d.get('_total_bytes_estimate_str') or '?'
                                msg = f"[DOWNLOADING] {speed} | ETA: {eta} | {size}"
                                progress_callback(pct, msg)
                            except Exception as pe:
                                pass  # Silently ignore progress parsing errors
                        elif d['status'] == 'finished' and progress_callback:
                            progress_callback(95.0, "[POST-PROCESSING] Merging audio/video...")
                        elif d['status'] == 'postprocessing' and progress_callback:
                            progress_callback(98.0, "[POST-PROCESSING] Finalizing format conversion...")

                    current_opts['progress_hooks'] = [progress_hook]
                    
                    with yt_dlp.YoutubeDL(current_opts) as ydl:
                        self.log(f"[YT-DLP] Downloading with format: {fmt}")
                        ydl.download([url])
                        success = True
                    
                    self.log(f"[SUCCESS] Download completed with {strategy['name']} strategy, format L{fallback_idx}")
                    if progress_callback:
                        progress_callback(100.0, "[DONE] Download successful!")
                    
                except Exception as e:
                    last_error = str(e)
                    error_brief = last_error[:150]
                    
                    self.log(f"[FAILED L{fallback_idx}] {strategy['name']}: {error_brief}")
                    self.log(f"[DEBUG] Full error: {last_error}")
                    self.log(f"[DEBUG] Traceback: {traceback.format_exc()}")
                    
                    # Handle specific errors
                    if "rate-limited" in str(e).lower() or "429" in str(e):
                        if progress_callback:
                            progress_callback(0, "[RATE-LIMITED] Cooling down 45s...")
                        self.log(f"[RATE-LIMIT] Waiting 45 seconds...")
                        time.sleep(45)
                        continue
                    
                    if "Netscape format" in str(e):
                        self.last_detailed_error = "Cookie file is invalid or corrupt. Must be Netscape format."
                        raise Exception(self.last_detailed_error)
                    
                    # Handle audio extraction failures
                    if "exit code -22" in str(e) or "audio conversion failed" in str(e).lower():
                        self.log(f"[AUDIO-ERROR] FFmpeg audio conversion failed")
                        self.log(f"[AUDIO-FIX] Try alternative format: -f wav or -f m4a")
                        # Continue to next strategy which may have different audio handling
                        continue
                    
                    # Continue to next fallback format
        
        if not success:
            msg = f"Download exhausted all {attempt_count} format/strategy attempts. Last error: {last_error}"
            self.last_detailed_error = msg
            self.log(f"[FATAL] {msg}")
            raise Exception(msg)
        
        return True
