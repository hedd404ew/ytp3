"""Command-line interface for YTP3Downloader."""

import os
import sys
import argparse

from ytp3.core.engine import YTP3Engine
from ytp3.utils.system import SystemDoctor, PathManager


def setup_parser():
    """Setup CLI argument parser."""
    p = argparse.ArgumentParser(
        description="YTP3Downloader - Modern YouTube downloader",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "https://www.youtube.com/watch?v=..."
  %(prog)s -a -f mp3 "https://www.youtube.com/playlist?list=..."
  %(prog)s -o ~/Downloads "https://www.youtube.com/watch?v=..."
        """
    )
    
    p.add_argument("url", nargs="?", help="YouTube URL to download")
    p.add_argument("-a", "--audio", action="store_true", help="Download audio only")
    p.add_argument("-f", "--format", help="Output format (mp4, mkv, mp3, m4a, etc.)")
    p.add_argument("-q", "--quality", choices=["best", "high", "medium", "low"], default="best", help="Video quality (best=any, high=max 1080p, medium=max 720p, low=max 480p)")
    p.add_argument("-o", "--output", help="Output directory")
    p.add_argument("--no-meta", action="store_true", help="Don't embed metadata")
    p.add_argument("--no-thumb", action="store_true", help="Don't embed thumbnail")
    p.add_argument("--subs", action="store_true", help="Download subtitles")
    p.add_argument("--geo", action="store_true", help="Enable geo-bypass")
    p.add_argument("--reverse", action="store_true", help="Reverse playlist order")
    p.add_argument("--force-ffmpeg", action="store_true", help="Force FFmpeg concat postprocessor for merging streams")
    p.add_argument("--cookies-browser", help="Extract cookies from browser (chrome, firefox, edge, brave)")
    p.add_argument("--cookies-file", help="Path to Netscape format cookie file")
    
    return p


def cli_progress(pct, msg):
    """Display CLI progress bar."""
    bar_len = 30
    filled = int(pct / 100 * bar_len)
    bar = '█' * filled + '-' * (bar_len - filled)
    sys.stdout.write(f"\r[{bar}] {pct:.1f}% | {msg[:40].ljust(40)}")
    sys.stdout.flush()


def cli_log(msg):
    """Log message in CLI mode."""
    print(f"\n[LOG] {msg}")


def run_cli(args):
    """Execute CLI mode."""
    print("\n--- YTP3Downloader [CLI MODE] ---\n")
    
    # Setup output path
    save_path = args.output if args.output else PathManager.get_default_path()
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    print(f"[INFO] Output: {save_path}")
    
    # Run diagnostics
    doctor = SystemDoctor()
    caps = doctor.run_diagnostics(save_path)
    
    missing = doctor.get_missing_criticals()
    if missing:
        print(f"[WARN] Missing Criticals: {', '.join(missing)}")
    
    # Build download options
    opts = {
        'outtmpl': os.path.join(save_path, '%(playlist_index)s - %(title)s.%(ext)s'),
        'ignoreerrors': True,
        'add_metadata': not args.no_meta,
        'writesubtitles': args.subs,
        'geo_bypass': args.geo,
        'playlistreverse': args.reverse,
        'format_quality': args.quality,  # Pass quality to engine
        'progress_hooks': [],
        'logger': None,
    }
    
    # Handle authentication
    if args.cookies_browser:
        opts['cookiesfrombrowser'] = (args.cookies_browser, None, None, None)
    if args.cookies_file:
        opts['cookiefile'] = args.cookies_file
    
    # Handle format
    if args.audio:
        fmt = args.format or 'mp3'
        print(f"[AUDIO] Mode ({fmt})")
        opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': fmt
            }]
        })
    else:
        fmt = args.format or 'mp4'
        quality = args.quality
        print(f"[VIDEO] Mode ({fmt}) | Quality: {quality}")
        
        # Engine handles format selection with fallbacks via FORMAT_FALLBACKS
        # Just set a base format and let engine manage degradation
        opts.update({
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': fmt,
            'format_quality': quality,
        })
        
        # Critical merge settings
        opts['prefer_ffmpeg'] = True
        opts['postprocessor_args'] = ['-c:v', 'copy', '-c:a', 'aac', '-loglevel', 'verbose']
    
    # Add postprocessors
    if 'postprocessors' not in opts:
        opts['postprocessors'] = []
    
    # NOTE: Thumbnail embedding disabled due to compatibility issues (exit code -22)
    # Users will get video with audio and metadata instead
    
    # Add metadata (but allow failures)
    if not args.no_meta:
        opts['postprocessors'].append({
            'key': 'FFmpegMetadata',
            'add_chapters': False  # Disable chapter adding to reduce complexity
        })
    
    # Download
    engine = YTP3Engine(opts, caps, log_callback=cli_log)
    
    print(f"\n[INFO] Processing: {args.url}")
    print(f"[CONFIG] Mode: VIDEO | Format: {args.format or 'mp4'} | Quality: {args.quality}")
    print(f"[CONFIG] FFmpeg Preferred: {args.force_ffmpeg}")
    print("")
    
    try:
        engine.download_single_item(args.url, cli_progress)
        print("\n\n[SUCCESS] Download completed successfully!")
    except Exception as e:
        print(f"\n\n[ERROR] Download failed!")
        print(f"[ERROR] Error message: {e}")
        
        # Show detailed error if available from engine
        if hasattr(engine, 'last_detailed_error') and engine.last_detailed_error:
            print(f"[DEBUG] Detailed error: {engine.last_detailed_error}")
        
        print("\n[TROUBLESHOOTING]")
        print("  1. Check your internet connection")
        print("  2. Try with --force-ffmpeg flag")
        print("  3. Try a different quality: -q low -q medium")
        print("  4. Video may be geo-blocked: try --geo flag")
        print("  5. Check if FFmpeg is installed: ffmpeg -version")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = setup_parser()
    args = parser.parse_args()
    
    if args.url:
        run_cli(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
