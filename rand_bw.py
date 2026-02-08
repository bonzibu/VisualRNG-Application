import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
from typing import Callable, Tuple
import math
import random

# ==================== CONFIGURATION ====================
GRID_W, GRID_H = 120, 120
PIXEL = 5
ANIMATION_SPEED = 0.8  # seconds for full animation

# Sophisticated color palette - Scientific Elegance
COLORS = {
    # Backgrounds
    "bg_primary": "#0a0e17",
    "bg_secondary": "#0f1419",
    "bg_tertiary": "#141921",
    "surface": "#1a1f2e",
    "surface_elevated": "#202536",
    
    # Accents
    "accent_primary": "#00d4ff",
    "accent_secondary": "#0099ff",
    "accent_tertiary": "#006bb3",
    "accent_glow": "#00ffff",
    
    # Status colors
    "success": "#00ff88",
    "warning": "#ffaa00",
    "error": "#ff4466",
    
    # Text
    "text_primary": "#e8edf4",
    "text_secondary": "#a8b3c7",
    "text_tertiary": "#6b7a93",
    "text_disabled": "#3d4555",
    
    # Borders & Dividers
    "border": "#2a3140",
    "border_focus": "#00d4ff",
    "divider": "#1e2533",
}

# Typography - Distinctive and professional
FONT_DISPLAY = ("JetBrains Mono", 24, "bold")
FONT_TITLE = ("Helvetica Neue", 16, "bold")
FONT_BODY = ("SF Pro Display", 13)
FONT_MONO = ("JetBrains Mono", 12)
FONT_LABEL = ("SF Pro Display", 11)
FONT_SMALL = ("SF Pro Display", 10)

# ==================== RNG ALGORITHMS ====================
def lcg(s: int) -> Tuple[int, int]:
    """Linear Congruential Generator (classic PRNG)"""
    return (s * 9301 + 49297) % 233280, 233280

def park_miller(s: int) -> Tuple[int, int]:
    """Park-Miller minimal standard generator"""
    return (s * 16807) % 2147483647, 2147483647

def xorshift(s: int) -> Tuple[int, int]:
    """Xorshift algorithm (fast & effective)"""
    s ^= (s << 13) & 0xFFFFFFFF
    s ^= (s >> 17)
    s ^= (s << 5) & 0xFFFFFFFF
    return s & 0xFFFFFFFF, 0xFFFFFFFF

def multiply_with_carry(s: int) -> Tuple[int, int]:
    """Multiply-with-carry generator"""
    a = 4294957665
    c = (s >> 32) & 0xFFFFFFFF
    x = s & 0xFFFFFFFF
    result = (a * x + c) & 0xFFFFFFFFFFFFFFFF
    return result, 0xFFFFFFFFFFFFFFFF
    
ALGORITHMS = {
    "Linear Congruential (LCG)": {
        "func": lcg,
        "desc": "Classic PRNG used in many systems",
        "color": "#00d4ff"
    },
    "Park-Miller": {
        "func": park_miller,
        "desc": "Minimal standard, good statistical properties",
        "color": "#00ff88"
    },
    "Xorshift": {
        "func": xorshift,
        "desc": "Fast bitwise operation-based generator",
        "color": "#ffaa00"
    },
    "Multiply-with-Carry": {
        "func": multiply_with_carry,
        "desc": "High-quality long-period generator",
        "color": "#ff4466"
    }
}

# ==================== UTILITY FUNCTIONS ====================
def value_to_color(v: int, mod: int, algorithm_color: str) -> str:
    """Convert RNG value to sophisticated grayscale with subtle accent tint"""
    ratio = v / mod
    base_gray = int(ratio * 200 + 20)
    
    # Add subtle color tint based on algorithm
    r = int(int(algorithm_color[1:3], 16) * 0.1 + base_gray * 0.9)
    g = int(int(algorithm_color[3:5], 16) * 0.1 + base_gray * 0.9)
    b = int(int(algorithm_color[5:7], 16) * 0.1 + base_gray * 0.9)
    
    return f"#{min(r, 255):02x}{min(g, 255):02x}{min(b, 255):02x}"

def ease_out_cubic(t: float) -> float:
    """Cubic ease-out for smooth animations"""
    return 1 - pow(1 - t, 3)

def ease_in_out_quart(t: float) -> float:
    """Quartic ease-in-out for button animations"""
    return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 4) / 2

def draw_rounded_rect(canvas, x1, y1, x2, y2, radius, **kwargs):
    """Draw a rounded rectangle on canvas"""
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)

# ==================== MAIN APPLICATION ====================
class RNGVisualizerPro:
    def __init__(self, root):
        self.root = root
        self.current_algorithm = tk.StringVar(value="Linear Congruential (LCG)")
        self.is_generating = False
        self.animation_id = None
        
        self._setup_window()
        self._create_layout()
        self._create_header()
        self._create_sidebar()
        self._create_visualization_area()
        self._create_stats_panel()
        self._setup_key_bindings()
        
    # ==================== WINDOW SETUP ====================
    def _setup_window(self):
        """Configure main window"""
        self.root.title("RNG Visualizer Pro")
        self.root.geometry("1400x900")
        self.root.configure(bg=COLORS["bg_primary"])
        self.root.resizable(True, True)
        
        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (900 // 2)
        self.root.geometry(f"1400x900+{x}+{y}")
        
    # ==================== LAYOUT ====================
    def _create_layout(self):
        """Create main layout structure"""
        # Header
        self.header = tk.Frame(self.root, bg=COLORS["bg_secondary"], height=80)
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)
        
        # Content area
        self.content = tk.Frame(self.root, bg=COLORS["bg_primary"])
        self.content.pack(fill="both", expand=True)
        
        # Sidebar
        self.sidebar = tk.Frame(self.content, bg=COLORS["bg_secondary"], width=320)
        self.sidebar.pack(fill="y", side="left")
        self.sidebar.pack_propagate(False)
        
        # Main area
        self.main_area = tk.Frame(self.content, bg=COLORS["bg_primary"])
        self.main_area.pack(fill="both", expand=True, side="left")
        
        # Stats panel (right)
        self.stats_panel = tk.Frame(self.content, bg=COLORS["bg_secondary"], width=280)
        self.stats_panel.pack(fill="y", side="right")
        self.stats_panel.pack_propagate(False)
        
    # ==================== HEADER ====================
    def _create_header(self):
        """Create application header"""
        # Title
        title_frame = tk.Frame(self.header, bg=COLORS["bg_secondary"])
        title_frame.pack(side="left", padx=30)
        
        tk.Label(
            title_frame,
            text="RNG VISUALIZER",
            font=FONT_DISPLAY,
            fg=COLORS["accent_primary"],
            bg=COLORS["bg_secondary"]
        ).pack(anchor="w")
        
        tk.Label(
            title_frame,
            text="RNG Analysis & Visualization - Developed By Bonzibu",
            font=FONT_SMALL,
            fg=COLORS["text_tertiary"],
            bg=COLORS["bg_secondary"]
        ).pack(anchor="w")
        
        # Version badge
        badge = tk.Label(
            self.header,
            text="BETA-V0.0.1",
            font=FONT_SMALL,
            fg=COLORS["text_tertiary"],
            bg=COLORS["surface"],
            padx=12,
            pady=4
        )
        badge.pack(side="right", padx=30)
        
    # ==================== SIDEBAR ====================
    def _create_sidebar(self):
        """Create control sidebar"""
        # Algorithm Selection
        tk.Label(
            self.sidebar,
            text="ALGORITHM",
            font=FONT_LABEL,
            fg=COLORS["text_tertiary"],
            bg=COLORS["bg_secondary"]
        ).pack(anchor="w", padx=24, pady=(30, 10))
        
        self._create_algorithm_selector()
        
        # Seed Input
        tk.Label(
            self.sidebar,
            text="SEED VALUE",
            font=FONT_LABEL,
            fg=COLORS["text_tertiary"],
            bg=COLORS["bg_secondary"]
        ).pack(anchor="w", padx=24, pady=(30, 10))
        
        self._create_seed_input()
        
        # Generate Button
        self._create_generate_button()
        
        # Quick Actions
        
    def _create_algorithm_selector(self):
        """Create algorithm selection dropdown"""
        selector_frame = tk.Frame(self.sidebar, bg=COLORS["bg_secondary"])
        selector_frame.pack(fill="x", padx=24, pady=5)
        
        for name, data in ALGORITHMS.items():
            self._create_algorithm_option(selector_frame, name, data)
    
    def _create_algorithm_option(self, parent, name, data):
        """Create individual algorithm option"""
        option_canvas = tk.Canvas(
            parent,
            height=70,
            bg=COLORS["bg_secondary"],
            highlightthickness=0
        )
        option_canvas.pack(fill="x", pady=4)
        
        # Background
        bg_color = COLORS["surface"] if self.current_algorithm.get() == name else COLORS["bg_tertiary"]
        rect = draw_rounded_rect(
            option_canvas, 0, 0, 272, 70, 12,
            fill=bg_color,
            outline=""
        )
        
        # Color indicator
        option_canvas.create_rectangle(
            0, 0, 4, 70,
            fill=data["color"],
            outline=""
        )
        
        # Text
        title_text = option_canvas.create_text(
            20, 22,
            text=name,
            anchor="w",
            fill=COLORS["text_primary"],
            font=FONT_BODY
        )
        
        desc_text = option_canvas.create_text(
            20, 48,
            text=data["desc"],
            anchor="w",
            fill=COLORS["text_tertiary"],
            font=FONT_SMALL
        )
        
        # Interaction
        def on_click(e):
            self.current_algorithm.set(name)
            self._refresh_algorithm_selector()
        
        def on_enter(e):
            option_canvas.itemconfig(rect, fill=COLORS["surface"])
            option_canvas.configure(cursor="hand2")
        
        def on_leave(e):
            bg = COLORS["surface"] if self.current_algorithm.get() == name else COLORS["bg_tertiary"]
            option_canvas.itemconfig(rect, fill=bg)
            option_canvas.configure(cursor="")
        
        option_canvas.bind("<Button-1>", on_click)
        option_canvas.bind("<Enter>", on_enter)
        option_canvas.bind("<Leave>", on_leave)
        
        # Store reference
        option_canvas.algo_name = name
        
    def _refresh_algorithm_selector(self):
        """Refresh algorithm selector appearance"""
        for widget in self.sidebar.winfo_children():
            if isinstance(widget, tk.Frame):
                for canvas in widget.winfo_children():
                    if isinstance(canvas, tk.Canvas) and hasattr(canvas, 'algo_name'):
                        selected = canvas.algo_name == self.current_algorithm.get()
                        # This is simplified - in production you'd store item IDs
                        canvas.delete("all")
                        self._redraw_algorithm_option(canvas, canvas.algo_name, selected)
    
    def _redraw_algorithm_option(self, canvas, name, selected):
        """Redraw algorithm option"""
        data = ALGORITHMS[name]
        bg_color = COLORS["surface"] if selected else COLORS["bg_tertiary"]
        
        draw_rounded_rect(canvas, 0, 0, 272, 70, 12, fill=bg_color, outline="")
        canvas.create_rectangle(0, 0, 4, 70, fill=data["color"], outline="")
        canvas.create_text(20, 22, text=name, anchor="w", fill=COLORS["text_primary"], font=FONT_BODY)
        canvas.create_text(20, 48, text=data["desc"], anchor="w", fill=COLORS["text_tertiary"], font=FONT_SMALL)
        
    def _create_seed_input(self):
        """Create seed input field"""
        input_canvas = tk.Canvas(
            self.sidebar,
            height=50,
            bg=COLORS["bg_secondary"],
            highlightthickness=0
        )
        input_canvas.pack(fill="x", padx=24, pady=5)
        
        draw_rounded_rect(
            input_canvas, 0, 0, 272, 50, 12,
            fill=COLORS["surface"],
            outline=""
        )
        
        self.seed_entry = tk.Entry(
            input_canvas,
            bg=COLORS["surface"],
            fg=COLORS["text_primary"],
            font=FONT_MONO,
            relief="flat",
            insertbackground=COLORS["accent_primary"],
            bd=0
        )
        self.seed_entry.insert(0, "12345")
        
        input_canvas.create_window(
            16, 25,
            anchor="w",
            window=self.seed_entry,
            width=240
        )
        
        # Focus effects
        def on_focus_in(e):
            input_canvas.configure(highlightbackground=COLORS["border_focus"], highlightthickness=2)
        
        def on_focus_out(e):
            input_canvas.configure(highlightthickness=0)
        
        self.seed_entry.bind("<FocusIn>", on_focus_in)
        self.seed_entry.bind("<FocusOut>", on_focus_out)
        
    def _create_generate_button(self):
        """Create main generate button"""
        button_frame = tk.Frame(self.sidebar, bg=COLORS["bg_secondary"])
        button_frame.pack(fill="x", padx=24, pady=30)
        
        self.gen_button_canvas = tk.Canvas(
            button_frame,
            height=56,
            bg=COLORS["bg_secondary"],
            highlightthickness=0
        )
        
        self.gen_button_canvas.pack(fill="x")
        
        self._draw_generate_button(COLORS["accent_primary"])
        
        self.gen_button_canvas.bind("<Button-1>", lambda e: self.generate_visualization())
        self.gen_button_canvas.bind("<Enter>", lambda e: self._draw_generate_button(COLORS["accent_glow"]))
        self.gen_button_canvas.bind("<Leave>", lambda e: self._draw_generate_button(COLORS["accent_primary"]))
        self.gen_button_canvas.configure(cursor="hand2")
    
    def _draw_generate_button(self, color):
        """Draw generate button"""
        self.gen_button_canvas.delete("all")
        
        draw_rounded_rect(
            self.gen_button_canvas,
            0, 0, 272, 56, 14,
            fill=color,
            outline=""
        )
        
        self.gen_button_canvas.create_text(
            136, 28,
            text="GENERATE",
            fill=COLORS["bg_primary"],
            font=FONT_TITLE
        )
        
    def _create_quick_actions(self, parent):
        """Create quick action buttons (right panel)"""
        tk.Label(
            parent,
            text="QUICK ACTIONS",
            font=FONT_LABEL,
            fg=COLORS["text_tertiary"],
            bg=COLORS["bg_secondary"]
        ).pack(anchor="w", padx=24, pady=(30, 10))
    
        actions_frame = tk.Frame(parent, bg=COLORS["bg_secondary"])
        actions_frame.pack(fill="x", padx=24)
    
        self._create_action_button(actions_frame, "Random Seed", self._randomize_seed)
        self._create_action_button(actions_frame, "Clear Grid", self._clear_grid)

        
    def _create_action_button(self, parent, text, command):
        """Create individual action button"""
        btn_canvas = tk.Canvas(
            parent,
            height=40,
            bg=COLORS["bg_secondary"],
            highlightthickness=0
        )
        btn_canvas.pack(fill="x", pady=4)
        
        rect = draw_rounded_rect(
            btn_canvas, 0, 0, 272, 40, 10,
            fill=COLORS["bg_tertiary"],
            outline=""
        )
        
        btn_canvas.create_text(
            119, 20,
            text=text,
            fill=COLORS["text_secondary"],
            font=FONT_BODY
        )
        
        def on_click(e):
            command()
        
        def on_enter(e):
            btn_canvas.itemconfig(rect, fill=COLORS["surface"])
            btn_canvas.configure(cursor="hand2")
        
        def on_leave(e):
            btn_canvas.itemconfig(rect, fill=COLORS["bg_tertiary"])
            btn_canvas.configure(cursor="")
        
        btn_canvas.bind("<Button-1>", on_click)
        btn_canvas.bind("<Enter>", on_enter)
        btn_canvas.bind("<Leave>", on_leave)
    
    # ==================== VISUALIZATION AREA ====================
    def _create_visualization_area(self):
        """Create main visualization canvas"""
        # Container
        viz_container = tk.Frame(self.main_area, bg=COLORS["bg_primary"])
        viz_container.pack(expand=True, fill="both", padx=40, pady=40)
        
        # Canvas card
        canvas_width = GRID_W * PIXEL + 60
        canvas_height = GRID_H * PIXEL + 60
        
        self.viz_card = tk.Canvas(
            viz_container,
            width=canvas_width,
            height=canvas_height,
            bg=COLORS["bg_primary"],
            highlightthickness=0
        )
        self.viz_card.pack()
        
        # Card background
        draw_rounded_rect(
            self.viz_card,
            0, 0,
            canvas_width, canvas_height,
            24,
            fill=COLORS["bg_secondary"],
            outline=""
        )
        
        # Grid canvas
        self.grid_canvas = tk.Canvas(
            self.viz_card,
            width=GRID_W * PIXEL,
            height=GRID_H * PIXEL,
            bg=COLORS["bg_tertiary"],
            highlightthickness=0
        )
        
        self.viz_card.create_window(
            30, 30,
            anchor="nw",
            window=self.grid_canvas
        )
        
        # Status label
        self.status_label = tk.Label(
            viz_container,
            text="Ready to generate visualization",
            font=FONT_BODY,
            fg=COLORS["text_tertiary"],
            bg=COLORS["bg_primary"]
        )
        self.status_label.pack(pady=15)
        
    # ==================== STATS PANEL ====================
    def _create_stats_panel(self):
        """Create statistics panel"""
        tk.Label(
            self.stats_panel,
            text="STATISTICS",
            font=FONT_LABEL,
            fg=COLORS["text_tertiary"],
            bg=COLORS["bg_secondary"]
        ).pack(anchor="w", padx=24, pady=(30, 20))

        # Stats container
        self.stats_container = tk.Frame(self.stats_panel, bg=COLORS["bg_secondary"])
        self.stats_container.pack(fill="x", padx=24)

        self.stats_items = {}
        stats_labels = [
            ("Final Value", "—"),
            ("Iterations", "—"),
            ("Min Value", "—"),
            ("Max Value", "—"),
            ("Generation Time", "—")
        ]

        for label, value in stats_labels:
            self._create_stat_item(label, value)
        
        self._create_quick_actions(self.stats_panel)
    
    def _create_stat_item(self, label, initial_value):
        """Create individual stat item"""
        item_canvas = tk.Canvas(
            self.stats_container,
            height=80,
            bg=COLORS["bg_secondary"],
            highlightthickness=0
        )
        item_canvas.pack(fill="x", pady=6)
        
        draw_rounded_rect(
            item_canvas, 0, 0, 232, 80, 12,
            fill=COLORS["surface"],
            outline=""
        )
        
        item_canvas.create_text(
            20, 24,
            text=label.upper(),
            anchor="w",
            fill=COLORS["text_tertiary"],
            font=FONT_SMALL
        )
        
        value_text = item_canvas.create_text(
            20, 52,
            text=initial_value,
            anchor="w",
            fill=COLORS["text_primary"],
            font=FONT_MONO
        )
        
        self.stats_items[label] = (item_canvas, value_text)
    
    def _update_stat(self, label, value):
        """Update a stat value"""
        if label in self.stats_items:
            canvas, text_id = self.stats_items[label]
            canvas.itemconfig(text_id, text=str(value))
    
    # ==================== GENERATION ====================
    def generate_visualization(self):
        """Generate RNG visualization"""
        if self.is_generating:
            return
        
        self.is_generating = True
        self.status_label.config(text="Generating...", fg=COLORS["accent_primary"])
        
        # Get algorithm
        algo_name = self.current_algorithm.get()
        algo_func = ALGORITHMS[algo_name]["func"]
        algo_color = ALGORITHMS[algo_name]["color"]
        
        # Get seed
        try:
            seed = int(self.seed_entry.get())
        except ValueError:
            seed = random.randint(1, 999999)
            self.seed_entry.delete(0, tk.END)
            self.seed_entry.insert(0, str(seed))
        
        # Clear grid
        self.grid_canvas.delete("all")
        
        # Track stats
        start_time = time.time()
        min_val = float('inf')
        max_val = 0
        
        # Generate grid
        s = seed
        last_value = s
        
        for y in range(GRID_H):
            for x in range(GRID_W):
                s, mod = algo_func(s)
                last_value = s
                
                min_val = min(min_val, s)
                max_val = max(max_val, s)
                
                color = value_to_color(s, mod, algo_color)
                
                self.grid_canvas.create_rectangle(
                    x * PIXEL, y * PIXEL,
                    (x + 1) * PIXEL, (y + 1) * PIXEL,
                    fill=color,
                    outline=""
                )
        
        # Update stats
        gen_time = time.time() - start_time
        self._update_stat("Final Value", f"{last_value:,}")
        self._update_stat("Iterations", f"{GRID_W * GRID_H:,}")
        self._update_stat("Min Value", f"{min_val:,}")
        self._update_stat("Max Value", f"{max_val:,}")
        self._update_stat("Generation Time", f"{gen_time:.3f}s")
        
        self.status_label.config(
            text=f"Generated {GRID_W * GRID_H:,} values using {algo_name}",
            fg=COLORS["success"]
        )
        
        self.is_generating = False
    
    # ==================== QUICK ACTIONS ====================
    def _randomize_seed(self):
        """Generate random seed"""
        new_seed = random.randint(1, 999999)
        self.seed_entry.delete(0, tk.END)
        self.seed_entry.insert(0, str(new_seed))
        self.status_label.config(text=f"Seed randomized to {new_seed}", fg=COLORS["text_tertiary"])
    
    def _clear_grid(self):
        """Clear the visualization grid"""
        self.grid_canvas.delete("all")
        for label in self.stats_items:
            self._update_stat(label, "—")
        self.status_label.config(text="Grid cleared", fg=COLORS["text_tertiary"])
    
    def _export_data(self):
        """Export visualization data"""
        messagebox.showinfo(
            "Export Data",
            "Export functionality would save the current visualization\nand statistics to a file (CSV, PNG, or JSON)."
        )
    
    # ==================== KEY BINDINGS ====================
    def _setup_key_bindings(self):
        """Setup keyboard shortcuts"""
        self.root.bind("<Return>", lambda e: self.generate_visualization())
        self.root.bind("<Control-r>", lambda e: self._randomize_seed())
        self.root.bind("<Control-c>", lambda e: self._clear_grid())


# ==================== MAIN ====================
if __name__ == "__main__":
    root = tk.Tk()
    root.state("zoomed")   # <-- makes window start maximized
    app = RNGVisualizerPro(root)
    root.mainloop()