"""Main GUI application."""

import os
import sys
import threading
import concurrent.futures
import random
import time
from io import BytesIO

try:
    import customtkinter as ctk
    from PIL import Image
    import requests
except ImportError:
    raise ImportError("Required packages missing. Install with: pip install customtkinter pillow requests")

from .components import RetroProgressBar, VideoItemRow
from ytp3.core.engine import YTP3Engine
from ytp3.utils.system import ConfigManager, SystemDoctor, PathManager


class YTP3App(ctk.CTk):
    """Main GUI application window."""
    
    # Color scheme
    BG_GRAY = "#C0C0C0"
    NAVY = "#000080"
    
    # Concurrency settings
    IMAGE_LOADER = concurrent.futures.ThreadPoolExecutor(max_workers=4)
    
    def __init__(self):
        """Initialize the application."""
        super().__init__()
        self.title("YTP3Downloader")
        self.geometry("900x700")
        
        ctk.set_appearance_mode("Light")
        self.configure(fg_color=self.BG_GRAY)
        
        # Initialize managers
        self.doctor = SystemDoctor()
        self.cfg = ConfigManager()
        self.caps = {}
        self.queue_items = []
        
        # Setup window
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Build UI
        self.create_sidebar()
        self.create_tabs()
        
        # Startup checks
        self.after(100, self.check_first_run)

    def check_first_run(self):
        """Perform first-run initialization."""
        if not self.cfg.config_file:
            self.cfg.initialize(is_portable=True)
        
        self.load_settings()
        self.run_startup_checks()

    def run_startup_checks(self):
        """Run system diagnostics."""
        self.caps = self.doctor.run_diagnostics(self.path_entry.get())
        missing = self.doctor.get_missing_criticals()
        
        if missing:
            self.health_btn.configure(text="[!] Check Deps", text_color="red")
        else:
            self.health_btn.configure(text="[OK] System OK", text_color="green")

    def create_sidebar(self):
        """Create the left sidebar with controls."""
        self.sidebar = ctk.CTkFrame(
            self, width=180, corner_radius=0, fg_color=self.BG_GRAY,
            border_width=2, border_color="white"
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        
        # Title
        ctk.CTkLabel(
            self.sidebar, text="YTP3", font=("Arial Black", 18),
            text_color=self.NAVY
        ).pack(pady=(15, 5))
        
        # Mode selector
        self.mode_var = ctk.StringVar(value="Video")
        self._create_combo_group(
            "Mode", ["Video", "Audio"], self.mode_var, self.on_mode_change
        )
        
        # Format selector
        self.fmt_var = ctk.StringVar(value="mp4")
        self.fmt_menu = self._create_combo_group(
            "Format", ["mp4", "mkv", "webm"], self.fmt_var
        )
        
        # Quality selector (video mode only)
        self.quality_var = ctk.StringVar(value="best")
        self.quality_menu = self._create_combo_group(
            "Quality", ["best", "high", "medium", "low"], self.quality_var
        )
        
        # Force FFmpeg checkbox
        self.chk_force_ffmpeg = self._create_checkbox_inline("Force FFmpeg Merge")
        
        # Save path
        ctk.CTkLabel(
            self.sidebar, text="Save Path", font=("Arial", 10, "bold"),
            text_color="black", anchor="w"
        ).pack(fill="x", padx=10, pady=(10, 0))
        
        self.path_entry = ctk.CTkEntry(
            self.sidebar, corner_radius=0, border_color="gray",
            fg_color="white", text_color="black", height=24
        )
        self.path_entry.pack(padx=10, pady=2)
        
        ctk.CTkButton(
            self.sidebar, text="Browse...", command=self.browse_path,
            fg_color=self.BG_GRAY, text_color="black", border_width=2,
            border_color="white", hover_color="#D0D0D0", height=24, corner_radius=0
        ).pack(padx=10, pady=2)
        
        # Concurrency slider
        ctk.CTkLabel(
            self.sidebar, text="Threads", font=("Arial", 10, "bold"),
            text_color="black", anchor="w"
        ).pack(fill="x", padx=10, pady=(10, 0))
        
        self.conc_slider = ctk.CTkSlider(
            self.sidebar, from_=1, to=6, number_of_steps=5,
            command=self.update_conc_label, button_color=self.NAVY,
            progress_color="gray"
        )
        self.conc_slider.set(2)
        self.conc_slider.pack(padx=10, pady=(5, 0))
        
        self.conc_lbl = ctk.CTkLabel(
            self.sidebar, text="2", font=("Arial", 10), text_color="black"
        )
        self.conc_lbl.pack()
        
        # Health status button
        self.health_btn = ctk.CTkButton(
            self.sidebar, text="Checking...", fg_color=self.BG_GRAY,
            text_color="black", border_width=2, border_color="gray",
            hover_color="#D0D0D0", corner_radius=0, command=self.show_health
        )
        self.health_btn.pack(side="bottom", padx=10, pady=10)
        
        # Start button
        self.btn_start = ctk.CTkButton(
            self.sidebar, text="START", fg_color=self.NAVY, text_color="white",
            border_width=2, border_color="white", hover_color="#0000A0",
            corner_radius=0, height=40, font=("Arial", 12, "bold"),
            command=self.start_download
        )
        self.btn_start.pack(side="bottom", padx=10, pady=(0, 10))

    def _create_combo_group(self, label, values, var, cmd=None):
        """Create a labeled combo box."""
        ctk.CTkLabel(
            self.sidebar, text=label, font=("Arial", 10, "bold"),
            text_color="black", anchor="w"
        ).pack(fill="x", padx=10, pady=(10, 0))
        
        box = ctk.CTkOptionMenu(
            self.sidebar, values=values, variable=var, command=cmd,
            fg_color="white", button_color=self.BG_GRAY,
            button_hover_color="#A0A0A0", text_color="black",
            corner_radius=0, height=24
        )
        box.pack(padx=10, pady=2)
        
        return box

    def create_tabs(self):
        """Create the main tabbed interface."""
        self.tabs = ctk.CTkTabview(
            self, fg_color=self.BG_GRAY, text_color="black",
            segmented_button_fg_color="#A0A0A0",
            segmented_button_selected_color=self.BG_GRAY,
            segmented_button_selected_hover_color=self.BG_GRAY,
            segmented_button_unselected_color="#D0D0D0", corner_radius=0
        )
        self.tabs.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        self.tab_queue = self.tabs.add("Queue")
        self.tab_auth = self.tabs.add("Auth")
        self.tab_adv = self.tabs.add("Settings")
        self.tab_log = self.tabs.add("Log")
        
        self.build_queue_tab()
        self.build_auth_tab()
        self.build_adv_tab()
        self.build_log_tab()

    def build_queue_tab(self):
        """Build the Queue tab UI."""
        # URL input frame
        frame = ctk.CTkFrame(self.tab_queue, fg_color="transparent")
        frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(frame, text="URL:", text_color="black").pack(side="left", padx=5)
        
        self.url_box = ctk.CTkEntry(
            frame, corner_radius=0, fg_color="white",
            text_color="black", border_color="gray"
        )
        self.url_box.pack(side="left", fill="x", expand=True, padx=5)
        
        self.btn_analyze = ctk.CTkButton(
            frame, text="Analyze", command=self.fetch_metadata,
            fg_color=self.BG_GRAY, text_color="black", border_width=2,
            border_color="white", corner_radius=0, width=80
        )
        self.btn_analyze.pack(side="right", padx=5)
        
        # Control buttons
        ctrl = ctk.CTkFrame(self.tab_queue, fg_color="transparent", height=30)
        ctrl.pack(fill="x", pady=5)
        
        ctk.CTkButton(
            ctrl, text="[x] All", width=60, height=20,
            fg_color=self.BG_GRAY, text_color="black", border_width=1,
            corner_radius=0, command=lambda: self.set_all_checks(True)
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            ctrl, text="[ ] None", width=60, height=20,
            fg_color=self.BG_GRAY, text_color="black", border_width=1,
            corner_radius=0, command=lambda: self.set_all_checks(False)
        ).pack(side="left", padx=5)
        
        self.lbl_queue_count = ctk.CTkLabel(ctrl, text="0 Items", text_color="black")
        self.lbl_queue_count.pack(side="right", padx=10)
        
        # Queue items list
        self.queue_scroll = ctk.CTkScrollableFrame(
            self.tab_queue, fg_color="white", corner_radius=0,
            border_width=2, border_color="#808080"
        )
        self.queue_scroll.pack(fill="both", expand=True, pady=5)
        
        # Progress tracking
        self.total_prog = RetroProgressBar(self.tab_queue, height=15)
        self.total_prog.set(0)
        self.total_prog.pack(fill="x", pady=5)
        
        self.total_status = ctk.CTkLabel(
            self.tab_queue, text="Ready", text_color="black"
        )
        self.total_status.pack()

    def build_auth_tab(self):
        """Build the Authentication tab UI."""
        ctk.CTkLabel(
            self.tab_auth, text="Authentication", font=("Arial", 12, "bold"),
            text_color="black"
        ).pack(anchor="w", pady=10)
        
        # Browser cookies
        self.browser_var = ctk.StringVar(value="None")
        ctk.CTkLabel(
            self.tab_auth, text="Browser Cookies:", text_color="black"
        ).pack(anchor="w", padx=10)
        
        ctk.CTkOptionMenu(
            self.tab_auth, values=["None", "chrome", "firefox", "edge", "brave"],
            variable=self.browser_var, fg_color="white", text_color="black",
            button_color="gray", corner_radius=0
        ).pack(anchor="w", padx=10, pady=5)
        
        # Cookie file
        ctk.CTkLabel(
            self.tab_auth, text="Cookie File:", text_color="black"
        ).pack(anchor="w", padx=10, pady=(20, 0))
        
        self.cookie_entry = ctk.CTkEntry(
            self.tab_auth, fg_color="white", text_color="black", corner_radius=0
        )
        self.cookie_entry.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(
            self.tab_auth, text="Browse", command=self.browse_cookie,
            fg_color=self.BG_GRAY, text_color="black", border_width=2, corner_radius=0
        ).pack(anchor="e", padx=10)

    def build_adv_tab(self):
        """Build the Settings/Advanced tab UI."""
        self.chk_meta = self._create_checkbox("Embed Metadata")
        self.chk_thumb = self._create_checkbox("Embed Thumbnail")
        self.chk_subs = self._create_checkbox("Download Subtitles")
        self.chk_sponsor = self._create_checkbox("SponsorBlock (Wait for FFmpeg)")
        self.chk_archive = self._create_checkbox("Download Archive")
        self.chk_geo = self._create_checkbox("Geo-Bypass")

    def _create_checkbox(self, text):
        """Create a styled checkbox."""
        c = ctk.CTkCheckBox(
            self.tab_adv, text=text, text_color="black",
            corner_radius=0, border_color="black", fg_color="white",
            checkmark_color="black", hover_color="#C0C0C0"
        )
        c.pack(anchor="w", pady=5, padx=10)
        return c

    def _create_checkbox_inline(self, text):
        """Create a styled checkbox for sidebar."""
        c = ctk.CTkCheckBox(
            self.sidebar, text=text, text_color="black",
            corner_radius=0, border_color="black", fg_color=self.BG_GRAY,
            checkmark_color="black", hover_color="#D0D0D0"
        )
        c.pack(anchor="w", pady=3, padx=10)
        return c

    def build_log_tab(self):
        """Build the Log tab UI."""
        self.log_box = ctk.CTkTextbox(
            self.tab_log, font=("Consolas", 10), fg_color="white",
            text_color="black", corner_radius=0, border_width=2, border_color="gray"
        )
        self.log_box.pack(fill="both", expand=True)

    def log(self, msg):
        """Log a message to the log box."""
        self.log_box.insert("end", f"{msg}\n")
        self.log_box.see("end")

    def update_conc_label(self, val):
        """Update concurrency display label."""
        self.conc_lbl.configure(text=f"{int(val)}")

    def on_mode_change(self, m):
        """Handle mode change event."""
        if m == "Audio":
            self.fmt_menu.configure(values=["mp3", "m4a", "wav"])
            self.fmt_var.set("mp3")
        else:
            self.fmt_menu.configure(values=["mp4", "mkv", "webm"])
            self.fmt_var.set("mp4")
            # Show quality and ffmpeg options for video mode
            if hasattr(self, 'quality_var'):
                self.quality_menu.configure(state="normal")
            if hasattr(self, 'chk_force_ffmpeg'):
                self.chk_force_ffmpeg.configure(state="normal")

    def browse_path(self):
        """Open directory browser for download path."""
        p = ctk.filedialog.askdirectory()
        if p:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, p)

    def browse_cookie(self):
        """Open file browser for cookie file."""
        p = ctk.filedialog.askopenfilename()
        if p:
            try:
                with open(p, 'r') as f:
                    header = f.read(50)
                    if "Netscape" not in header and "# HTTP Cookie File" not in header and not header.startswith("#"):
                        self.log("[WARN] Warning: This doesn't look like a Netscape cookie file!")
            except:
                pass
            
            self.cookie_entry.delete(0, "end")
            self.cookie_entry.insert(0, p)

    def show_health(self):
        """Show system health status dialog."""
        msg = f"FFmpeg: {self.caps['ffmpeg']}\nJS Runtime: {self.caps['js_runtime']}\nInternet: {self.caps['internet']}"
        dialog = ctk.CTkToplevel(self)
        dialog.geometry("300x200")
        ctk.CTkLabel(dialog, text=msg).pack(pady=20)

    def load_settings(self):
        """Load settings from configuration."""
        d = self.cfg.load()
        
        # Paths and basic settings
        self.path_entry.delete(0, "end")
        self.path_entry.insert(0, d.get("save_path", ""))
        
        # URL (from last session)
        self.url_box.delete(0, "end")
        self.url_box.insert(0, d.get("last_url", ""))
        
        # Concurrency slider
        self.conc_slider.set(d.get("concurrency", 2))
        self.update_conc_label(d.get("concurrency", 2))
        
        # Mode and format
        self.mode_var.set(d.get("mode", "Video"))
        self.fmt_var.set(d.get("format", "mp4"))
        
        # Quality
        self.quality_var.set(d.get("quality", "best"))
        
        # Checkboxes (toggles)
        t = d.get("toggles", {})
        for c, k in [(self.chk_meta, "meta"), (self.chk_thumb, "thumb"),
                     (self.chk_subs, "subs"), (self.chk_sponsor, "sponsor"),
                     (self.chk_geo, "geo"), (self.chk_force_ffmpeg, "force_ffmpeg")]:
            if t.get(k):
                c.select()
            else:
                c.deselect()
        
        # Authentication settings
        self.browser_var.set(d.get("browser_cookies", "None"))
        self.cookie_entry.delete(0, "end")
        self.cookie_entry.insert(0, d.get("cookie_file", ""))

    def set_all_checks(self, val):
        """Set all queue items to checked/unchecked."""
        for item in self.queue_items:
            item.var_selected.set(val)
            item.toggle_selection()

    def fetch_metadata(self):
        """Fetch metadata for URL in the input box."""
        url = self.url_box.get().strip()
        if not url:
            return
        
        # Clear queue
        for widget in self.queue_scroll.winfo_children():
            widget.destroy()
        self.queue_items.clear()
        
        self.btn_analyze.configure(state="disabled", text="Wait...")
        
        def run():
            auth_opts = {}
            if self.browser_var.get() != "None":
                auth_opts['cookiesfrombrowser'] = (self.browser_var.get(), None, None, None)
            if self.cookie_entry.get().strip():
                auth_opts['cookiefile'] = self.cookie_entry.get().strip()
            
            engine = YTP3Engine(auth_opts, self.caps, log_callback=self.log)
            try:
                self.log(f"[INFO] Analyzing: {url}")
                entries = engine.resolve_metadata(url)
                self.after(0, lambda: self._populate_queue(entries, engine))
            except Exception as e:
                self.log(f"[ERROR] Fetch Error: {e}")
                self.btn_analyze.configure(state="normal", text="Analyze")
        
        threading.Thread(target=run, daemon=True).start()

    def _populate_queue(self, entries, engine_ref):
        """Populate queue with metadata entries."""
        for idx, entry in enumerate(entries):
            item = VideoItemRow(self.queue_scroll, entry, idx, engine_ref)
            item.pack(fill="x", pady=2)
            self.queue_items.append(item)
        
        self.lbl_queue_count.configure(text=f"{len(entries)} Items")
        self.btn_analyze.configure(state="normal", text="Analyze")
        self.log(f"[INFO] Loaded {len(entries)} items.")

    def start_download(self):
        """Start downloading selected queue items."""
        # Filter out invalid items (missing URLs) and log them
        all_selected = [i for i in self.queue_items if i.var_selected.get()]
        selected_items = [i for i in all_selected if i.is_valid]
        
        if not selected_items:
            return self.log("[WARN] No valid items selected (check for [INVALID URL] labels).")
        
        # Warn about skipped invalid items
        invalid_count = len(all_selected) - len(selected_items)
        if invalid_count > 0:
            self.log(f"[WARN] Skipping {invalid_count} item(s) with invalid/missing URLs")
        
        self.btn_start.configure(state="disabled", text="Running...")
        self.total_prog.start_animation()
        
        path = self.path_entry.get()
        quality = self.quality_var.get()
        
        opts = {
            'outtmpl': os.path.join(path, '%(title)s.%(ext)s'),
            'ignoreerrors': True,
            'add_metadata': self.chk_meta.get(),
            'writesubtitles': self.chk_subs.get(),
            'embedsubtitles': self.chk_subs.get(),
            'geo_bypass': self.chk_geo.get(),
            'format_quality': quality,  # Pass quality to engine
            'prefer_ffmpeg': True,
            'postprocessor_args': ['-c:v', 'copy', '-c:a', 'aac', '-loglevel', 'verbose'],
            'progress_hooks': [],
            'logger': None,
        }
        
        if self.chk_sponsor.get():
            opts['sponsorblock_remove'] = 'all'
        
        if self.browser_var.get() != "None":
            opts['cookiesfrombrowser'] = (self.browser_var.get(), None, None, None)
        elif self.cookie_entry.get().strip():
            opts['cookiefile'] = self.cookie_entry.get().strip()
        
        # Log download configuration
        self.log(f"[CONFIG] Mode: {'AUDIO' if self.mode_var.get() == 'Audio' else 'VIDEO'}")
        self.log(f"[CONFIG] Format: {self.fmt_var.get()}")
        self.log(f"[CONFIG] Quality: {quality}")
        self.log(f"[CONFIG] Force FFmpeg: {self.chk_force_ffmpeg.get()}")
        self.log(f"[CONFIG] Concurrent Downloads: {int(self.conc_slider.get())}")
        self.log("")
        
        if self.mode_var.get() == "Audio":
            opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': self.fmt_var.get()
                }]
            })
            self.log("[AUDIO] Audio-only mode enabled")
        else:
            # Video mode - let engine handle format selection with fallbacks
            opts.update({
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': self.fmt_var.get(),
            })
            self.log(f"[VIDEO] Video+Audio mode with 5-layer fallback enabled")
        
        # Initialize postprocessors
        if 'postprocessors' not in opts:
            opts['postprocessors'] = []
        
        # NOTE: Thumbnail embedding disabled due to compatibility issues (exit code -22)
        # Users will get video with audio and metadata instead
        
        # Add metadata (but allow failures)
        if self.chk_meta.get():
            opts['postprocessors'].append({
                'key': 'FFmpegMetadata',
                'add_chapters': False  # Disable chapter adding to reduce complexity
            })
        
        max_workers = int(self.conc_slider.get())
        
        def run_queue():
            engine = YTP3Engine(opts, self.caps, log_callback=self.log)
            
            self.log(f"[QUEUE] Starting download of {len(selected_items)} item(s) with {max_workers} worker(s)")
            self.log("")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {}
                for idx, item in enumerate(selected_items, 1):
                    item.update_status(0, "Queued...")
                    url = item.url
                    title = item.info.get('title', 'Unknown')
                    
                    self.log(f"[QUEUE {idx}/{len(selected_items)}] Queuing: {title[:60]}")
                    
                    future = executor.submit(engine.download_single_item, url, item.update_status)
                    futures[future] = (item, title)
                    time.sleep(random.randint(2, 4))
                
                self.log("")
                completed = 0
                failed = 0
                
                for future in concurrent.futures.as_completed(futures):
                    item, title = futures[future]
                    try:
                        future.result()
                        item.update_status(100, "Done")
                        self.log(f"[SUCCESS] ✓ {title[:60]}")
                        completed += 1
                    except Exception as e:
                        item.update_status(0, "Failed")
                        failed += 1
                        error_msg = str(e)[:100]
                        self.log(f"[FAILED] ✗ {title[:60]}")
                        self.log(f"         Error: {error_msg}")
                        
                        # Show detailed error if available from engine
                        if hasattr(engine, 'last_detailed_error') and engine.last_detailed_error:
                            self.log(f"         Details: {engine.last_detailed_error[:150]}")
                    
                    prog_val = (completed + failed) / len(selected_items)
                    self.total_prog.set(prog_val)
                    self.total_status.configure(text=f"{completed} OK | {failed} Failed | {len(selected_items) - completed - failed} Pending")
            
            self.log("")
            self.log(f"[COMPLETE] Queue finished: {completed} successful, {failed} failed")
            self.total_prog.stop_animation()
            self.total_prog.set(1.0)
            self.btn_start.configure(state="normal", text="START")
        
        threading.Thread(target=run_queue, daemon=True).start()

    def on_close(self):
        """Handle window close event."""
        # Save basic settings
        self.cfg.data["save_path"] = self.path_entry.get()
        self.cfg.data["concurrency"] = int(self.conc_slider.get())
        
        # Save URL
        self.cfg.data["last_url"] = self.url_box.get()
        
        # Save mode and format
        self.cfg.data["mode"] = self.mode_var.get()
        self.cfg.data["format"] = self.fmt_var.get()
        
        # Save quality
        self.cfg.data["quality"] = self.quality_var.get()
        
        # Save toggle settings
        toggles = {
            "meta": self.chk_meta.get(),
            "thumb": self.chk_thumb.get(),
            "subs": self.chk_subs.get(),
            "sponsor": self.chk_sponsor.get(),
            "geo": self.chk_geo.get(),
            "force_ffmpeg": self.chk_force_ffmpeg.get(),
        }
        self.cfg.data["toggles"] = toggles
        
        # Save authentication settings
        self.cfg.data["browser_cookies"] = self.browser_var.get()
        self.cfg.data["cookie_file"] = self.cookie_entry.get()
        
        self.cfg.save()
        self.destroy()


def run_gui():
    """Launch the GUI application."""
    app = YTP3App()
    app.mainloop()
