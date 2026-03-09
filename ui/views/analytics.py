import tkinter as tk
import datetime
import math
from theme import Colors, Fonts, Metrics
from ui_components import GlassCard, RoundedRect
from ui.views.base import BaseView
import database

class SmoothBar(tk.Canvas):
    def __init__(self, master, x, y, width, max_height, value, max_value, day_label, accent_color, *args, **kwargs):
        super().__init__(master, *args, bg=Colors.BACKGROUND, highlightthickness=0, **kwargs)
        self.bar_x = x
        self.bar_y = y
        self.bar_w = width
        self.max_h = max_height
        self.val = value
        self.max_val = max_value if max_value > 0 else 1
        self.day_label = day_label
        self.accent_color = accent_color
        
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)
        
        self.draw(hover=False)

    def draw(self, hover=False):
        self.delete("all")
        
        # Calculate Height
        h = (self.val / self.max_val) * self.max_h
        if h < 4: h = 4 # Minimum height so empty days show a dot
        
        start_y = self.max_h - h
        
        # Draw Background Track (optional, looks cleaner without it or with very faint one)
        # RoundedRect.draw(self, 0, 0, self.bar_w, self.max_h, self.bar_w/2, Colors.SURFACE_2)
        
        # Draw Bar
        bar_color = self.accent_color if not hover else Colors.TEXT_PRIMARY
        if self.val == 0:
            bar_color = Colors.SURFACE_3 # Empty state color
        
        # Rounded Rect for bar. Radius is half the width to make them pill shaped
        radius = self.bar_w / 2
        
        # We need to simulate drawing on the parent, but since we are a distinct Canvas, our coordinates start at 0
        # Actually, it's easier if SmoothBar *is* the canvas for just this column, or if the parent manages it.
        # Let's assume this canvas is sized exactly to the column (width, max_h + text_space)
        pass 
        

class ActivityChart(tk.Canvas):
    def __init__(self, master, width=600, height=250, data=None, labels=None):
        super().__init__(master, width=width, height=height, 
                         bg=Colors.BACKGROUND, highlightthickness=0)
        self.width = width
        self.height = height
        self.data = data or [0,0,0,0,0,0,0]
        self.labels = labels or ["M", "T", "W", "T", "F", "S", "S"]
        self.hovered_idx = -1
        
        self.bind("<Motion>", self.on_motion)
        self.bind("<Leave>", self.on_leave)
        
        # Initial animation state could go here, for now static
        self.draw()

    def on_motion(self, e):
        # Determine which bar is hovered based on X coordinate
        bar_w = 40
        spacing = (self.width - 100) / 7
        start_x = 50
        
        found = -1
        for i in range(len(self.data)):
            x_center = start_x + (i * spacing) + (bar_w/2)
            # if within 30px of center
            if abs(e.x - x_center) < (spacing/2):
                if e.y < self.height - 30: # Above text labels
                    found = i
                    break
                    
        if found != self.hovered_idx:
            self.hovered_idx = found
            self.draw()

    def on_leave(self, e):
        if self.hovered_idx != -1:
            self.hovered_idx = -1
            self.draw()

    def draw(self):
        self.delete("all")
        
        # 1. Background Panel for the chart
        RoundedRect.draw(self, 1, 1, self.width-2, self.height-2, 20, Colors.SURFACE_1, outline=Colors.SURFACE_3)
        
        max_val = max(self.data) if self.data else 100
        if max_val == 0: max_val = 100
        
        bar_w = 40
        spacing = (self.width - 100) / 7
        start_x = 50
        max_h = self.height - 100 # Leaves room for top tooltip and bottom text
        base_y = self.height - 40
        
        # Draw Y-Axis guides (Subtle)
        guide_y = base_y - max_h
        self.create_line(40, guide_y, self.width-40, guide_y, fill=Colors.SURFACE_3, dash=(4, 4))
        self.create_line(40, base_y, self.width-40, base_y, fill=Colors.SURFACE_3, dash=(4, 4))
        
        # Draw Bars
        for i, val in enumerate(self.data):
            x = start_x + (i * spacing)
            h = (val / max_val) * max_h
            if h < 6: h = 6 # Minimum pill shape
            y = base_y - h
            
            is_hovered = (i == self.hovered_idx)
            
            # Colors
            col = Colors.ACCENT
            if is_hovered:
                col = Colors.TEXT_PRIMARY # Highlight color
            elif val == 0:
                col = Colors.SURFACE_3
                
            # Draw Pill/Bar
            RoundedRect.draw(self, x, y, bar_w, h, bar_w/2, col)
            
            # Label
            text_col = Colors.TEXT_PRIMARY if is_hovered else Colors.TEXT_SECONDARY
            font = Fonts.BODY_L if is_hovered else Fonts.BODY
            self.create_text(x + bar_w/2, base_y + 20, text=self.labels[i], fill=text_col, font=font)
            
            # Tooltip
            if is_hovered:
                # Draw tooltip bubble above bar
                tt_y = y - 25
                tt_text = f"{int(val)}m" # Assuming minutes
                
                # Check bounds
                if tt_y < 15: tt_y = 15
                
                # Draw little backdrop for text
                RoundedRect.draw(self, x - 5, tt_y - 12, bar_w + 10, 24, 8, Colors.SURFACE_2, outline=Colors.SURFACE_3)
                self.create_text(x + bar_w/2, tt_y, text=tt_text, fill=Colors.TEXT_PRIMARY, font=Fonts.CAPTION)

class AppleStatCard(tk.Canvas):
    def __init__(self, master, width=220, height=140, title="", value="", icon="", accent=Colors.ACCENT):
        super().__init__(master, width=width, height=height, 
                         bg=Colors.BACKGROUND, highlightthickness=0)
        self.width = width
        self.height = height
        self.title = title
        self.value = value
        self.icon = icon
        self.accent = accent
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)
        self.draw(hover=False)

    def draw(self, hover=False):
        self.delete("all")
        bg_col = Colors.SURFACE_2 if hover else Colors.SURFACE_1
        border_col = self.accent if hover else Colors.SURFACE_3
        
        # Shadow effect (fake)
        if hover:
            RoundedRect.draw(self, 2, 2, self.width, self.height, 16, "#000000") # Extremely basic shadow offset
            
        RoundedRect.draw(self, 0, 0, self.width, self.height, 16, 
                         bg_col, outline=border_col, width=1)
                         
        # Icon Circle
        self.create_oval(15, 15, 45, 45, fill=self.accent, outline="")
        self.create_text(30, 30, text=self.icon, fill="#000000", font=("Segoe UI Emoji", 12))
        
        # Title
        self.create_text(15, 65, text=self.title.upper(), fill=Colors.TEXT_TERTIARY, font=("Segoe UI", 9, "bold"), anchor="nw")
        
        # Big Value
        self.create_text(15, 85, text=self.value, fill=Colors.TEXT_PRIMARY, font=("Segoe UI", 28, "bold"), anchor="nw")

    def on_hover(self, e): self.draw(hover=True)
    def on_leave(self, e): self.draw(hover=False)

class AnalyticsView(BaseView):
    def __init__(self, master, app_context):
        super().__init__(master, app_context)
        self.configure(bg=Colors.BACKGROUND)
        self.setup_ui()
        self.refresh_data()

    def setup_ui(self):
        # 1. Scrollable Container
        container = tk.Canvas(self, bg=Colors.BACKGROUND, highlightthickness=0)
        container.pack(fill="both", expand=True)
        
        # 2. Content Frame
        content = tk.Frame(container, bg=Colors.BACKGROUND)
        initial_w = self.app.winfo_width()
        self.list_window = container.create_window((0,0), window=content, anchor="nw", width=initial_w)
        
        # 3. Wrapper (Centered)
        self.wrapper = tk.Frame(content, bg=Colors.BACKGROUND)
        self.wrapper.pack(pady=40, expand=True)
        
        # 1. Header
        tk.Label(self.wrapper, text="Analytics", font=("Segoe UI", 26, "bold"), bg=Colors.BACKGROUND, fg=Colors.TEXT_PRIMARY).pack(anchor="w", pady=(0, 20))
        
        # 2. Stats Grid (Apple style)
        # We need the total width of this grid to match Settings (which is ~600px or 700px in the screenshot).
        # Settings uses `width=600` for `SettingsGroup`.
        # Let's make 3 cards of width 180 + 10px padding = ~600px total width.
        stats_frame = tk.Frame(self.wrapper, bg=Colors.BACKGROUND)
        stats_frame.pack(fill="x", pady=(0, 30))
        
        self.card_streak = AppleStatCard(stats_frame, width=180, height=130, title="Current Streak", icon="🔥", accent=Colors.ACCENT)
        self.card_streak.grid(row=0, column=0, padx=(0, 30))
        
        self.card_focus = AppleStatCard(stats_frame, width=180, height=130, title="Total Focus Time", icon="⏳", accent=Colors.ACCENT)
        self.card_focus.grid(row=0, column=1, padx=(0, 30))
        
        self.card_xp = AppleStatCard(stats_frame, width=180, height=130, title="Total XP", icon="🌟", accent=Colors.NEON_YELLOW)
        self.card_xp.grid(row=0, column=2, padx=(0, 0)) # No right padding on last item
        
        # 3. Chart Section
        chart_header = tk.Frame(self.wrapper, bg=Colors.BACKGROUND)
        chart_header.pack(fill="x", pady=(10, 10))
        tk.Label(chart_header, text="Activity (Last 7 Days)", font=("Segoe UI", 16, "bold"), bg=Colors.BACKGROUND, fg=Colors.TEXT_SECONDARY).pack(side="left")
        
        self.chart_container = tk.Frame(self.wrapper, bg=Colors.BACKGROUND)
        self.chart_container.pack(fill="x", expand=False)
        # Width here should also be 600
        self.chart = ActivityChart(self.chart_container, width=600, height=250)
        self.chart.pack()

        # Responsive Layout & Scroll Logic
        def on_resize(event):
            container.itemconfig(self.list_window, width=event.width)
            content.update_idletasks()
            container.config(scrollregion=container.bbox("all"))
                 
        container.bind("<Configure>", on_resize)
        
        def on_mousewheel(event):
            container.yview_scroll(int(-1*(event.delta/120)), "units")
            
        def bind_scroll(e):
            container.bind_all("<MouseWheel>", on_mousewheel)
        def unbind_scroll(e):
            container.unbind_all("<MouseWheel>")
            
        container.bind("<Enter>", bind_scroll)
        container.bind("<Leave>", unbind_scroll)

    def refresh_data(self):
        # 1. Fetch History from Database
        try:
            logs = database.get_history_stats() # Returns up to 30 days ordered by date DESC
        except:
            logs = []
            
        # Parse last 7 days from today
        today = datetime.date.today()
        dates = [today - datetime.timedelta(days=i) for i in range(6, -1, -1)]
        labels = [d.strftime("%a") for d in dates] # "Mon", "Tue"...
        
        # Map DB logs to dates
        log_map = {l['date']: l for l in logs}
        
        chart_data = []
        for d in dates:
            d_str = d.strftime("%Y-%m-%d")
            if d_str in log_map:
                chart_data.append(log_map[d_str]['total_time_seconds'] / 60) # Minutes
            else:
                chart_data.append(0)
                
        # Calculate Aggregates
        items = self.app.blocks_manager.get_items()
        max_streak = 0
        total_time_all = 0
        
        for i in items:
            if hasattr(i, 'streak') and i.streak > max_streak: max_streak = i.streak
            if hasattr(i, 'total_minutes'): total_time_all += i.total_minutes
            
        # Overall completion rate logic removed to make room for XP display
        lifetime_xp = database.get_lifetime_xp()
            
        # 2. Update Cards
        self.card_streak.value = f"{max_streak} D"
        self.card_streak.draw()
        
        hours = total_time_all // 60
        mins = total_time_all % 60
        self.card_focus.value = f"{hours}h {mins}m"
        self.card_focus.draw()
        
        self.card_xp.value = f"{lifetime_xp:,}"
        self.card_xp.draw()

        # 3. Update Chart
        self.chart.data = chart_data
        self.chart.labels = labels
        self.chart.draw()
