import tkinter as tk
from theme import Colors, Fonts, Metrics
from ui.views.base import BaseView
from ui_components import RoundedRect
from modules.session_logger import compute_analytics


class AnalyticsView(BaseView):
    def __init__(self, master, app_context):
        super().__init__(master, app_context)
        self.configure(bg=Colors.BACKGROUND)
        
        # --- SCROLLABLE CONTAINER (same pattern as SettingsView) ---
        container = tk.Canvas(self, bg=Colors.BACKGROUND, highlightthickness=0)
        container.pack(fill="both", expand=True)
        
        content = tk.Frame(container, bg=Colors.BACKGROUND)
        initial_w = self.app.winfo_width()
        self.list_window = container.create_window((0, 0), window=content, anchor="nw", width=initial_w)
        
        wrapper = tk.Frame(content, bg=Colors.BACKGROUND)
        wrapper.pack(pady=40, expand=True)
        
        # Load data
        data = compute_analytics()
        
        # ── HEADER ──
        tk.Label(wrapper, text="Analytics", font=("Segoe UI", 26, "bold"),
                 bg=Colors.BACKGROUND, fg=Colors.TEXT_PRIMARY).pack(anchor="w", pady=(0, 28))
        
        # ── STATS ROW ──
        self._section_label(wrapper, "OVERVIEW")
        stats_frame = tk.Frame(wrapper, bg=Colors.BACKGROUND)
        stats_frame.pack(fill="x", pady=(0, 24))
        
        self._stat_tile(stats_frame, "Streak", f"{data['streak']} days", 0)
        self._stat_tile(stats_frame, "Focus This Week", f"{data['focus_hours_week']} hrs", 1)
        self._stat_tile(stats_frame, "Total XP", f"{data['total_xp']}", 2)
        
        for i in range(3):
            stats_frame.columnconfigure(i, weight=1, uniform="s")
        
        # ── DAILY FOCUS (last 7 days) ──
        self._section_label(wrapper, "DAILY FOCUS — LAST 7 DAYS")
        chart_frame = tk.Frame(wrapper, bg=Colors.SURFACE_1)
        chart_frame.pack(fill="x", pady=(0, 24))
        
        chart_canvas = tk.Canvas(chart_frame, bg=Colors.SURFACE_1, highlightthickness=0, height=180)
        chart_canvas.pack(fill="x", padx=16, pady=16)
        self.after(80, lambda: self._draw_chart(chart_canvas, data["daily_focus"]))
        
        # ── STREAK & BEST DAY ──
        self._section_label(wrapper, "THIS WEEK")
        bottom_frame = tk.Frame(wrapper, bg=Colors.BACKGROUND)
        bottom_frame.pack(fill="x", pady=(0, 24))
        
        # Streak tile with dots
        self._streak_tile(bottom_frame, data["streak"], data["streak_dots"], 0)
        # Best day tile
        self._best_day_tile(bottom_frame, data["best_day_hours"], data["best_day_name"], 1)
        
        for i in range(2):
            bottom_frame.columnconfigure(i, weight=1, uniform="b")
        
        # ── FOOTER ──
        total_label = f"{data['total_sessions']} sessions completed"
        tk.Label(wrapper, text=total_label, font=("Segoe UI", 10),
                 bg=Colors.BACKGROUND, fg=Colors.TEXT_TERTIARY).pack(pady=(8, 20))
        
        # Scroll setup (same as SettingsView)
        content.update_idletasks()
        container.configure(scrollregion=container.bbox("all"))
        
        def on_resize(event):
            container.itemconfig(self.list_window, width=event.width)
            content.update_idletasks()
            container.config(scrollregion=container.bbox("all"))
        container.bind("<Configure>", on_resize)
        
        def on_mousewheel(event):
            container.yview_scroll(int(-1 * (event.delta / 120)), "units")
        def bind_scroll(e):
            container.bind_all("<MouseWheel>", on_mousewheel)
        def unbind_scroll(e):
            container.unbind_all("<MouseWheel>")
        container.bind("<Enter>", bind_scroll)
        container.bind("<Leave>", unbind_scroll)

    # ── HELPERS ──
    
    def _section_label(self, parent, text):
        """Consistent section label (matches SettingsView)."""
        tk.Label(parent, text=text, font=("Segoe UI", 9, "bold"),
                 fg=Colors.TEXT_SECONDARY, bg=Colors.BACKGROUND
                 ).pack(anchor="w", padx=10, pady=(10, 5))

    def _stat_tile(self, parent, label, value, col):
        """Simple stat tile — surface card with label + big number."""
        tile = tk.Frame(parent, bg=Colors.SURFACE_1, padx=20, pady=18)
        tile.grid(row=0, column=col, padx=(0, 6) if col < 2 else 0, sticky="nsew")
        
        tk.Label(tile, text=label, font=("Segoe UI", 9),
                 bg=Colors.SURFACE_1, fg=Colors.TEXT_TERTIARY).pack(anchor="w")
        tk.Label(tile, text=value, font=("Segoe UI", 24, "bold"),
                 bg=Colors.SURFACE_1, fg=Colors.TEXT_PRIMARY).pack(anchor="w", pady=(6, 0))
    
    def _draw_chart(self, canvas, daily_data):
        """Minimal bar chart for last 7 days."""
        canvas.delete("all")
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        if w < 20:
            self.after(100, lambda: self._draw_chart(canvas, daily_data))
            return
        
        n = len(daily_data)
        if n == 0:
            return
        
        max_val = max((d["minutes"] for d in daily_data), default=0)
        max_val = max(max_val, 360)  # 6hr scale minimum
        
        chart_top = 10
        chart_bottom = h - 24
        chart_h = chart_bottom - chart_top
        slot_w = w / n
        bar_w = max(int(slot_w * 0.35), 12)
        
        for i, day in enumerate(daily_data):
            x_center = slot_w * i + slot_w / 2
            x1 = x_center - bar_w / 2
            x2 = x_center + bar_w / 2
            
            val = day["minutes"]
            bar_h = max((val / max_val) * chart_h, 3) if val > 0 else 3
            y_top = chart_bottom - bar_h
            
            fill = Colors.ACCENT if day["is_today"] else ("#333333" if val > 0 else "#1e1e1e")
            canvas.create_rectangle(x1, y_top, x2, chart_bottom, fill=fill, outline="")
            
            # Day label below
            lbl_color = Colors.ACCENT if day["is_today"] else Colors.TEXT_TERTIARY
            canvas.create_text(x_center, chart_bottom + 12, text=day["day"],
                             font=("Segoe UI", 8), fill=lbl_color)
            
            # Minutes label on top (if > 0)
            if val > 0:
                canvas.create_text(x_center, y_top - 8, text=f"{val}m",
                                 font=("Segoe UI", 7), fill=Colors.TEXT_TERTIARY)
    
    def _streak_tile(self, parent, streak, dots, col):
        """Streak tile with week dots."""
        tile = tk.Frame(parent, bg=Colors.SURFACE_1, padx=20, pady=18)
        tile.grid(row=0, column=col, padx=(0, 6) if col == 0 else 0, sticky="nsew")
        
        tk.Label(tile, text="Streak", font=("Segoe UI", 9),
                 bg=Colors.SURFACE_1, fg=Colors.TEXT_TERTIARY).pack(anchor="w")
        tk.Label(tile, text=f"{streak} days", font=("Segoe UI", 24, "bold"),
                 bg=Colors.SURFACE_1, fg=Colors.TEXT_PRIMARY).pack(anchor="w", pady=(6, 0))
        
        # Week dots row
        dots_row = tk.Frame(tile, bg=Colors.SURFACE_1)
        dots_row.pack(fill="x", pady=(14, 0))
        
        days = ["M", "T", "W", "T", "F", "S", "S"]
        for i, dot in enumerate(dots):
            col_f = tk.Frame(dots_row, bg=Colors.SURFACE_1)
            col_f.pack(side="left", expand=True, fill="x")
            
            if dot["is_today"]:
                color = Colors.ACCENT
            elif dot["filled"]:
                color = "#5C4520"
            else:
                color = "#222222"
            
            dot_c = tk.Canvas(col_f, bg=Colors.SURFACE_1, highlightthickness=0, width=20, height=4)
            dot_c.pack()
            dot_c.create_rectangle(0, 0, 20, 4, fill=color, outline="")
            
            tk.Label(col_f, text=days[i], font=("Segoe UI", 7),
                     bg=Colors.SURFACE_1, fg=Colors.TEXT_TERTIARY).pack(pady=(3, 0))
    
    def _best_day_tile(self, parent, hours, day_name, col):
        """Best day tile."""
        tile = tk.Frame(parent, bg=Colors.SURFACE_1, padx=20, pady=18)
        tile.grid(row=0, column=col, sticky="nsew")
        
        tk.Label(tile, text="Best Day", font=("Segoe UI", 9),
                 bg=Colors.SURFACE_1, fg=Colors.TEXT_TERTIARY).pack(anchor="w")
        
        val = f"{hours} hrs" if hours > 0 else "—"
        tk.Label(tile, text=val, font=("Segoe UI", 24, "bold"),
                 bg=Colors.SURFACE_1, fg=Colors.TEXT_PRIMARY).pack(anchor="w", pady=(6, 0))
        
        name = day_name if hours > 0 else "No sessions yet"
        tk.Label(tile, text=name, font=("Segoe UI", 10),
                 bg=Colors.SURFACE_1, fg=Colors.TEXT_TERTIARY).pack(anchor="w", pady=(8, 0))
