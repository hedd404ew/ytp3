"""UI Components for the GUI application."""

import colorsys

try:
    import customtkinter as ctk
except ImportError:
    raise ImportError("customtkinter is required. Install with: pip install customtkinter")


class RetroProgressBar(ctk.CTkProgressBar):
    """Animated retro-style progress bar with color cycling."""
    
    def __init__(self, *args, **kwargs):
        """Initialize the progress bar."""
        super().__init__(*args, **kwargs)
        self.configure(corner_radius=0, border_width=2, border_color="gray50")
        self.hue = 0
        self.running = False

    def start_animation(self):
        """Start the color animation."""
        if not self.running:
            self.running = True
            self.animate()

    def stop_animation(self):
        """Stop the color animation and reset to default color."""
        self.running = False
        self.configure(progress_color="#000080")

    def animate(self):
        """Animate the progress bar color."""
        if not self.running:
            return
        
        self.hue = (self.hue + 0.005) % 1.0
        rgb = colorsys.hsv_to_rgb(self.hue, 0.8, 0.9)
        color_hex = "#%02x%02x%02x" % (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
        self.configure(progress_color=color_hex)
        self.after(50, self.animate)


class VideoItemRow(ctk.CTkFrame):
    """UI component for displaying a single video item in the queue."""
    
    def __init__(self, parent, info_dict, idx, engine_ref):
        """
        Initialize video item row.
        
        Args:
            parent: Parent widget
            info_dict (dict): Video information dictionary
            idx (int): Item index
            engine_ref: Reference to download engine
        """
        super().__init__(parent, fg_color="#DFDFDF", corner_radius=0, border_width=2, border_color="white")
        self.info = info_dict
        self.url = info_dict.get('url') or info_dict.get('original_url')
        
        self.bind("<Button-1>", self.toggle_selection)
        self._create_widgets()
        self._load_thumbnail()

    def _create_widgets(self):
        """Create and layout UI widgets."""
        # Selection checkbox
        self.var_selected = ctk.BooleanVar(value=True)
        self.chk = ctk.CTkCheckBox(
            self, text="", variable=self.var_selected, width=20,
            corner_radius=0, border_width=2, border_color="#808080",
            fg_color="white", checkmark_color="black", hover_color="#C0C0C0"
        )
        self.chk.grid(row=0, column=0, padx=5, pady=10, rowspan=2, sticky="w")

        # Thumbnail placeholder
        self.thumb_lbl = ctk.CTkLabel(
            self, text="", width=80, height=45,
            fg_color="black", corner_radius=0
        )
        self.thumb_lbl.grid(row=0, column=1, padx=5, pady=5, rowspan=2)
        self.thumb_lbl.bind("<Button-1>", self.toggle_selection)

        # Title label
        title = self.info.get('title', 'Unknown Title')
        if len(title) > 55:
            title = title[:52] + "..."
        self.title_lbl = ctk.CTkLabel(
            self, text=title, font=("Arial", 11, "bold"),
            text_color="black", anchor="w"
        )
        self.title_lbl.grid(row=0, column=2, padx=5, pady=(5, 0), sticky="ew")
        self.title_lbl.bind("<Button-1>", self.toggle_selection)

        # Duration label
        duration = self.info.get('duration_string') or "?"
        self.meta_lbl = ctk.CTkLabel(
            self, text=f"Time: {duration}", font=("Arial", 10),
            text_color="#404040", anchor="w"
        )
        self.meta_lbl.grid(row=1, column=2, padx=5, pady=(0, 5), sticky="ew")
        self.meta_lbl.bind("<Button-1>", self.toggle_selection)

        # Progress bar
        self.prog_bar = ctk.CTkProgressBar(
            self, height=10, width=120, progress_color="#000080",
            fg_color="white", corner_radius=0, border_width=1, border_color="black"
        )
        self.prog_bar.set(0)
        self.prog_bar.grid(row=0, column=3, padx=5, pady=(10, 0), sticky="e")

        # Status label
        self.status_lbl = ctk.CTkLabel(
            self, text="Waiting...", font=("Arial", 9),
            text_color="#000000", width=120, anchor="e"
        )
        self.status_lbl.grid(row=1, column=3, padx=5, pady=(0, 5), sticky="e")

        self.grid_columnconfigure(2, weight=1)

    def toggle_selection(self, event=None):
        """Toggle the selection state of this item."""
        self.var_selected.set(not self.var_selected.get())
        color = "#FFFFFF" if self.var_selected.get() else "#DFDFDF"
        self.configure(fg_color=color)

    def _load_thumbnail(self):
        """Load and display thumbnail (async)."""
        thumb_url = None
        
        if 'thumbnails' in self.info:
            thumb_url = self.info['thumbnails'][-1].get('url') if self.info['thumbnails'] else None
        else:
            thumb_url = self.info.get('thumbnail')
        
        if thumb_url:
            # This will be handled by parent widget's executor
            pass

    def update_status(self, percent, msg):
        """
        Update download status and progress.
        
        Args:
            percent (float): Progress percentage (0-100)
            msg (str): Status message
        """
        self.prog_bar.set(percent / 100)
        self.status_lbl.configure(text=msg)
        
        if percent >= 100:
            self.status_lbl.configure(text="Complete", text_color="green")
