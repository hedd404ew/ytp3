"""Core download engine for YTP3Downloader."""

import time
import random
from .strategies import DownloadStrategy

try:
    import yt_dlp
except ImportError:
    raise ImportError("yt-dlp is required. Install with: pip install yt-dlp")


class YTP3Engine:
    """Main download engine handling metadata resolution and downloads."""
    
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
                        return results
                        
            except Exception as e:
                error_msg = str(e)
                
                # Handle cookie format errors
                if "Netscape format" in error_msg:
                    raise Exception("Invalid Cookie File. Must be Netscape format (not JSON).")
                
                last_error = error_msg
                
                # Retry on signature/availability errors
                if "Signatures" in error_msg or "not available" in error_msg:
                    self.log(f"[WARN] Metadata fetch failed with {strategy['name']}. Retrying next strategy...")
                    continue
                else:
                    break
        
        raise Exception(f"Metadata fetch failed after all attempts: {last_error}")

    def download_single_item(self, url, progress_callback=None):
        """
        Download a single video with retry strategies.
        
        Args:
            url (str): Video URL to download
            progress_callback (callable, optional): Callback for progress updates
            
        Raises:
            Exception: If download fails after all strategies
        """
        success = False
        last_error = ""
        
        # Random delay to avoid rate limiting
        time.sleep(random.uniform(0.5, 2.0))

        for strategy in self.strategies:
            if success:
                break
            
            current_opts = self.opts.copy()
            current_opts.update(strategy['extra'])
            
            # Add rate-limiting
            current_opts['sleep_interval'] = random.randint(3, 8)
            current_opts['max_sleep_interval'] = 15
            
            # Progress callback handler
            def progress_hook(d):
                if d['status'] == 'downloading' and progress_callback:
                    p = d.get('_percent_str', '0%').replace('%', '')
                    try:
                        pct = float(p)
                        speed = d.get('_speed_str', 'N/A')
                        eta = d.get('_eta_str', '?')
                        size = d.get('_total_bytes_str') or d.get('_total_bytes_estimate_str') or '?'
                        msg = f"{speed} | ETA: {eta} | {size}"
                        progress_callback(pct, msg)
                    except:
                        pass
                elif d['status'] == 'finished' and progress_callback:
                    progress_callback(100.0, "Finalizing conversion...")

            current_opts['progress_hooks'] = [progress_hook]
            current_opts['quiet'] = True
            current_opts['no_warnings'] = True

            try:
                with yt_dlp.YoutubeDL(current_opts) as ydl:
                    ydl.download([url])
                success = True
                
            except Exception as e:
                last_error = str(e)
                
                # Handle rate limiting
                if "rate-limited" in str(e).lower():
                    if progress_callback:
                        progress_callback(0, "Server Rate Limit Detected! Cooling down 60s...")
                    time.sleep(60)
                    continue
                
                # Handle cookie errors
                if "Netscape format" in str(e):
                    raise Exception("Cookie file is invalid or corrupt. Check format.")

                # Retry on extraction errors
                if "Requested format is not available" in str(e) or "Signatures" in str(e):
                    continue
                
                pass
        
        if not success:
            raise Exception(f"Download failed: {last_error}")
