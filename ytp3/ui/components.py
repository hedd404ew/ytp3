"""UI Components for the GUI application."""

import colorsys
from io import BytesIO

try:
    import customtkinter as ctk
    from PIL import Image
    import requests
except ImportError:
    raise ImportError("customtkinter, pillow, and requests required")


class RetroProgressBar(ctk.CTkFrame):
    """Modern retro-style progress bar with solid fill and status indicator."""
    
    def __init__(self, parent, *args, **kwargs):
        """Initialize the progress bar."""
        # Extract height before passing to parent
        self.custom_height = kwargs.pop('height', 30)
        
        super().__init__(parent, *args, **kwargs)
        self.configure(fg_color="#2D2D2D", corner_radius=4, height=self.custom_height)
        
        # Inner frame for the progress bar
        self.inner_frame = ctk.CTkFrame(self, fg_color="#2D2D2D", corner_radius=2)
        self.inner_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Progress fill
        self.fill = ctk.CTkFrame(self.inner_frame, fg_color="#0088FF", corner_radius=0)
        self.fill.pack(side="left", fill="y", expand=False)
        
        # Status label
        self.label = ctk.CTkLabel(
            self.inner_frame, 
            text="0%", 
            text_color="white",
            font=("Arial", 11, "bold"),
            bg_color="#2D2D2D"
        )
        self.label.pack(side="left", padx=8, fill="both", expand=True)
        
        self._value = 0
        self._max = 100
        self.running = False  # For compatibility with animation methods
        self.update_fill()

    def set(self, value):
        """Set progress bar value (compatible with CTkProgressBar)."""
        # Handle both 0-1 and 0-100 ranges
        if value <= 1:
            self._value = value * 100
        else:
            self._value = value
        self._value = max(0, min(self._value, 100))
        self.update_fill()

    def set_value(self, value):
        """Set progress bar value."""
        self._value = max(0, min(value, self._max))
        self.update_fill()

    def set_max(self, value):
        """Set maximum value."""
        self._max = max(1, value)
        self.update_fill()

    def start_animation(self):
        """Start animation (no-op for static progress bar)."""
        self.running = True

    def stop_animation(self):
        """Stop animation (no-op for static progress bar)."""
        self.running = False

    def update_fill(self):
        """Update the fill width based on current value."""
        percentage = (self._value / 100) * 100 if self._max == 100 else (self._value / self._max) * 100
        
        # Update color based on value
        if percentage < 33:
            color = "#FF6B6B"  # Red for slow progress
        elif percentage < 66:
            color = "#FFA500"  # Orange for medium progress
        else:
            color = "#00AA00"  # Green for good progress
        
        self.fill.configure(fg_color=color, width=int(percentage * 2.5))
        self.label.configure(text=f"{int(percentage)}%")


class RetroProgressBarAnimated(ctk.CTkProgressBar):
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
        self.thumb_image = None
        
        # BUG FIX: Flag invalid entries that lack URL
        self.is_valid = bool(self.url)
        
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
            self, text="[No Thumb]", width=80, height=45,
            fg_color="black", text_color="white", font=("Arial", 8),
            corner_radius=0
        )
        self.thumb_lbl.grid(row=0, column=1, padx=5, pady=5, rowspan=2)
        self.thumb_lbl.bind("<Button-1>", self.toggle_selection)

        # Title label
        title = self.info.get('title', 'Unknown Title')
        if len(title) > 55:
            title = title[:52] + "..."
        
        # Add visual indicator for invalid items
        if not self.is_valid:
            title = title + " [INVALID URL]"
            title_color = "#808080"
        else:
            title_color = "black"
            
        self.title_lbl = ctk.CTkLabel(
            self, text=title, font=("Arial", 11, "bold"),
            text_color=title_color, anchor="w"
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
        # Prevent selection of invalid items (missing URL)
        if not self.is_valid:
            return
            
        self.var_selected.set(not self.var_selected.get())
        color = "#FFFFFF" if self.var_selected.get() else "#DFDFDF"
        self.configure(fg_color=color)

    def _load_thumbnail(self):
        """Load and display thumbnail (non-blocking)."""
        try:
            thumb_url = None
            
            if 'thumbnails' in self.info and self.info['thumbnails']:
                # Get highest quality thumbnail
                thumb_url = self.info['thumbnails'][-1].get('url')
            else:
                thumb_url = self.info.get('thumbnail')
            
            if not thumb_url:
                return
            
            # Load thumbnail
            response = requests.get(thumb_url, timeout=5)
            response.raise_for_status()
            
            img_data = Image.open(BytesIO(response.content))
            img_data.thumbnail((80, 45), Image.Resampling.LANCZOS)
            
            self.thumb_image = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(80, 45))
            self.thumb_lbl.configure(image=self.thumb_image, text="")
            
        except Exception as e:
            # Silently fail - thumbnail is optional
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
