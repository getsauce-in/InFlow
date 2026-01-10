import tkinter as tk
from tkinter import ttk
import time
import math
from theme import Colors, Fonts, Metrics, Easing

class RoundedRect:
    @staticmethod
    def draw(canvas, x, y, w, h, radius, color, outline=None, width=0, tags=None):
        points = [
            x + radius, y,
            x + w - radius, y,
            x + w, y,
            x + w, y + radius,
            x + w, y + h - radius,
            x + w, y + h,
            x + w - radius, y + h,
            x + radius, y + h,
            x, y + h,
            x, y + h - radius,
            x, y + radius,
            x, y,
        ]
        return canvas.create_polygon(points, smooth=True, fill=color, outline=outline if outline else "", width=width, tags=tags)

class NeonButton(tk.Canvas):
    def __init__(self, master, text, command=None, width=160, height=44, 
                 accent_color=Colors.NEON_BLUE):
        super().__init__(master, width=width+10, height=height+10, 
                         bg=Colors.BACKGROUND, highlightthickness=0, cursor="hand2")
        self.command = command
        self.text = text
        self.w = width
        self.h = height
        self.accent = accent_color
        self.base_color = Colors.SURFACE_2
        
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)
        
        self.draw()

    def draw(self, offset=0, glow=False):
        try:
            self.delete("all")
            if glow:
                RoundedRect.draw(self, 5, 5, self.w, self.h, Metrics.CORNER_RADIUS, self.accent, tags="glow")
            fill_col = self.accent if glow else self.base_color
            # Fix: Black text on bright glow, White text on dark base
            text_col = "#000000" if glow else Colors.TEXT_PRIMARY
            
            RoundedRect.draw(self, 5, 5+offset, self.w, self.h, Metrics.CORNER_RADIUS, 
                             fill_col, outline=self.accent, width=1)
            self.create_text(5 + self.w/2, 5 + offset + self.h/2, text=self.text, 
                             fill=text_col, font=Fonts.BODY)
        except tk.TclError:
            pass

    def on_hover(self, e):
        try: self.draw(offset=-2, glow=True)
        except: pass

    def on_leave(self, e):
        try: self.draw(offset=0, glow=False)
        except: pass

    def on_click(self, e):
        try: self.draw(offset=1, glow=True)
        except: pass

    def on_release(self, e):
        try:
            self.draw(offset=0, glow=True)
            if self.command: self.command()
        except: pass

class GlassCard(tk.Canvas):
    def __init__(self, master, width=300, height=150, title="", subtitle="", icon=""):
        super().__init__(master, width=width+2, height=height+2, 
                         bg=Colors.BACKGROUND, highlightthickness=0)
        self.width = width
        self.height = height
        self.title = title
        self.subtitle = subtitle
        self.icon = icon
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)
        self.draw(hover=False)

    def draw(self, hover=False):
        self.delete("all")
        bg_col = Colors.SURFACE_2 if hover else Colors.SURFACE_1
        border_col = Colors.TEXT_SECONDARY if hover else Colors.SURFACE_3
        RoundedRect.draw(self, 1, 1, self.width, self.height, Metrics.CORNER_RADIUS, 
                         bg_col, outline=border_col, width=1)
        self.create_text(25, 30, text=self.icon, fill=Colors.NEON_YELLOW, font=("Segoe UI Emoji", 24), anchor="nw")
        self.create_text(25, 80, text=self.title, fill=Colors.TEXT_PRIMARY, font=Fonts.H2, anchor="nw")
        self.create_text(25, 115, text=self.subtitle, fill=Colors.TEXT_SECONDARY, font=Fonts.CAPTION, anchor="nw")

    def on_hover(self, e): self.draw(hover=True)
    def on_leave(self, e): self.draw(hover=False)

class IntegratedTitleBar(tk.Frame):
    def __init__(self, master, items, command_callback, window_control_callback, height=30):
        super().__init__(master, height=height, bg=Colors.NAV_BG)
        self.pack_propagate(False)
        self.items = items
        self.callback = command_callback
        self.win_callback = window_control_callback
        self.active_index = 0
        
        # 4. Bottom Border (Packed FIRST to span full width)
        self.border = tk.Frame(self, bg=Colors.SURFACE_3, height=1)
        self.border.pack(side="bottom", fill="x")
        
        # 1. Nav Area (Left)
        self.nav_frame = tk.Frame(self, bg=Colors.NAV_BG)
        self.nav_frame.pack(side="left", padx=15)
        
        self.nav_buttons = []
        for i, item in enumerate(items):
            # Text Button
            btn = tk.Label(self.nav_frame, text=item, font=Fonts.BODY, 
                           bg=Colors.NAV_BG, fg="#999999", cursor="hand2")
            btn.pack(side="left", padx=15)
            btn.bind("<Button-1>", lambda e, idx=i: self.set_active(idx))
            self.nav_buttons.append(btn)
            
        self.refresh_nav()
        
        # 2. Window Controls (Right)
        self.controls_frame = tk.Frame(self, bg=Colors.NAV_BG)
        self.controls_frame.pack(side="right", fill="y")
        
        # Minimize
        self.btn_min = self.create_control_btn("─", lambda e: self.win_callback("minimize"))
        # Maximize
        self.btn_max = self.create_control_btn("◻", lambda e: self.win_callback("maximize"))
        # Close
        self.btn_close = self.create_control_btn("✕", lambda e: self.win_callback("close"), hover_color="#E81123", hover_fg="white")

        # 3. Drag Area (Middle Filler)
        self.drag_frame = tk.Label(self, bg=Colors.NAV_BG) # Label captures clicks better than empty Frame sometimes
        self.drag_frame.pack(side="left", fill="both", expand=True)
        
        # Bind dragging to all containers to be safe
        for w in [self, self.drag_frame, self.nav_frame, self.controls_frame]:
            w.bind("<ButtonPress-1>", self.start_move)
            w.bind("<B1-Motion>", self.do_move)
        
    def create_control_btn(self, text, command, hover_color="#333333", hover_fg="white"):
        btn = tk.Label(self.controls_frame, text=text, font=("Segoe UI", 10), 
                       bg=Colors.NAV_BG, fg="#CCCCCC", width=5, height=2)
        btn.pack(side="left", fill="y")
        
        def on_enter(e): 
            btn.configure(bg=hover_color, fg=hover_fg)
        def on_leave(e): 
            btn.configure(bg=Colors.NAV_BG, fg="#CCCCCC")
            
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        btn.bind("<Button-1>", command)
        return btn

    def set_active(self, index):
        self.active_index = index
        self.refresh_nav()
        self.callback(self.items[index])

    def refresh_nav(self):
        for i, btn in enumerate(self.nav_buttons):
            if i == self.active_index:
                btn.configure(fg="white", font=Fonts.BODY_L)
            else:
                btn.configure(fg="#999999", font=Fonts.BODY)

    def start_move(self, event):
        self.start_x = event.x_root
        self.start_y = event.y_root
        try:
             self.win_x = self.winfo_toplevel().winfo_x()
             self.win_y = self.winfo_toplevel().winfo_y()
        except: 
             pass

    def do_move(self, event):
        deltax = event.x_root - self.start_x
        deltay = event.y_root - self.start_y
        x = self.win_x + deltax
        y = self.win_y + deltay
        self.winfo_toplevel().geometry(f"+{x}+{y}")

# Stub out MacToolbar/AppleModal if referenced elsewhere, but likely removed.
class MacToolbar(tk.Canvas): pass

class SettingsGroup(tk.Canvas):
    def __init__(self, master, rows, title=None, width=600):
        # Calculate height dynamicall based on rows
        # Row height = 50
        self.row_h = 50
        self.rows = rows # list of (label, value_text, command)
        self.h = len(rows) * self.row_h
        
        # Add Header space if title exists
        self.header_h = 40 if title else 0
        total_h = self.h + self.header_h
        
        super().__init__(master, width=width, height=total_h, bg=Colors.BACKGROUND, highlightthickness=0)
        self.width = width
        self.title = title
        
        self.draw()
        
    def draw(self):
        self.delete("all")
        
        # 1. Header
        y_offset = 0
        if self.title:
            self.create_text(20, 20, text=self.title.upper(), fill=Colors.TEXT_SECONDARY, 
                             font=("Segoe UI", 9, "bold"), anchor="w")
            y_offset = self.header_h
            
        # 2. Background (Rounded)
        bg_col = Colors.SURFACE_1
        RoundedRect.draw(self, 0, y_offset, self.width, self.h, Metrics.CORNER_RADIUS, bg_col)
        
        # 3. Rows
        current_y = y_offset
        for i, row_data in enumerate(self.rows):
            label, value, cmd = row_data
            
            # Hover/Click Logic
            # We'll use a tag for the whole row area
            row_tag = f"row_{i}"
            
            # Separator (if not last)
            if i < len(self.rows) - 1:
                self.create_line(20, current_y + self.row_h, self.width - 20, current_y + self.row_h, 
                                 fill=Colors.SURFACE_3, width=1)
            
            # Text - Label
            self.create_text(20, current_y + self.row_h/2, text=label, fill=Colors.TEXT_PRIMARY, 
                             font=Fonts.BODY_L, anchor="w", tags=row_tag)
            
            # Text - Value + Arrow
            right_text = value if value else "›"
            text_col = Colors.TEXT_SECONDARY if value else Colors.TEXT_TERTIARY
            if cmd and not value: right_text = "›" # Force arrow if clickable and no value
            
            self.create_text(self.width - 20, current_y + self.row_h/2, text=right_text, 
                             fill=text_col, font=Fonts.BODY, anchor="e", tags=row_tag)
            
            # Invisible hit box for events
            self.create_rectangle(0, current_y, self.width, current_y + self.row_h, 
                                  fill="", outline="", tags=row_tag)
            
            if cmd:
                self.tag_bind(row_tag, "<Button-1>", lambda e, c=cmd: c())
                self.tag_bind(row_tag, "<Enter>", lambda e, idx=i: self.on_row_hover(idx, True))
                self.tag_bind(row_tag, "<Leave>", lambda e, idx=i: self.on_row_hover(idx, False))
            
            current_y += self.row_h

    def on_row_hover(self, index, is_hover):
        # We can't easily change just the background rect of one slice in a rounded rect 
        # without complex drawing. For now, let's highlight text or draw a semi-transparent overlay.
        # Overlay approach:
        tags = f"hover_{index}"
        self.delete(tags)
        if is_hover:
            y = self.header_h + (index * self.row_h)
            # Draw rounded rect clipping? Too hard.
            # Simple highlight rect for now, maybe acceptable.
            # Actually, let's just make text brighter or Add a cursor change.
            self.config(cursor="hand2")
        else:
            self.config(cursor="")
class AppleModal(tk.Toplevel): pass
