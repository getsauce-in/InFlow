import tkinter as tk
from tkinter import ttk
import sys
import os
import datetime
import ctypes

from theme import Colors, Fonts, Metrics
from ui_components import IntegratedTitleBar, GlassCard, NeonButton
from modules.blocks import BlocksManager
from ui.views import HomeView, SettingsView
from ui.views.blocks import BlocksView
from ui.views.analytics import AnalyticsView
from active_view import ActiveRoutineView
import database

class Flow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("InFlow")
        
        # Frameless Window
        self.overrideredirect(True) 
        self.title_bar_height = 30
        
        # Application Icon
        try:
             icon_path = os.path.join("assets", "icon.ico")
             if os.path.exists(icon_path):
                 self.iconbitmap(default=icon_path)
             # Also set the photo icon for alt-tab / taskbar previews
             png_path = os.path.join("assets", "logo.png")
             if not os.path.exists(png_path):
                 png_path = os.path.join("assets", "icon.png")
             if os.path.exists(png_path):
                 self._icon_img = tk.PhotoImage(file=png_path)
                 self.iconphoto(True, self._icon_img)
        except Exception:
             pass
        
        # Windows Taskbar Fix — force frameless window to appear in taskbar
        try:
            import ctypes
            GWL_EXSTYLE = -20
            WS_EX_APPWINDOW = 0x00040000
            WS_EX_TOOLWINDOW = 0x00000080
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            style = style & ~WS_EX_TOOLWINDOW  # Remove "tool window" (hidden from taskbar)
            style = style | WS_EX_APPWINDOW     # Add "app window" (visible in taskbar)
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
            # Re-show to apply
            self.withdraw()
            self.after(10, self.deiconify)
        except Exception:
            pass
        
        # Initial Geometry
        self.window_w = Metrics.WINDOW_WIDTH
        self.window_h = Metrics.WINDOW_HEIGHT
        self.is_maximized = False
        self.pre_max_geom = f"{self.window_w}x{self.window_h}+100+100"
        
        self.geometry(self.pre_max_geom)
        self.configure(bg=Colors.BACKGROUND)
        
        # Windows Workaround for Taskbar Icon on Frameless Window
        try:
             hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
             style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
             style |= 0x00040000
             ctypes.windll.user32.SetWindowLongW(hwnd, -20, style)
        except:
             pass

        self.blocks_manager = BlocksManager()
        self.active_session = None  # Stores session state when switching tabs
        
        self.setup_ui()
        self.show_view("Sessions") 
        
        # Ensure window is visible
        self.deiconify()
        self.lift()
        self.focus_force()

    def window_action(self, action):
        if action == "close":
            self.destroy()
        elif action == "minimize":
            # Smooth minimize: hide → switch to standard frame → iconify → show
            self.withdraw()  # Hide instantly (no flicker)
            self.overrideredirect(False)
            self.iconify()
            self.bind("<Map>", self.on_restore_from_minimize)
        elif action == "maximize":
            self.toggle_maximize()

    def on_restore_from_minimize(self, event):
        if self.state() == "normal":
            self.unbind("<Map>")
            self.withdraw()  # Hide before switching frame mode
            self.overrideredirect(True)
            # Re-apply taskbar style
            try:
                 hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
                 style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
                 style = style & ~0x00000080  # Remove WS_EX_TOOLWINDOW
                 style = style | 0x00040000   # Add WS_EX_APPWINDOW
                 ctypes.windll.user32.SetWindowLongW(hwnd, -20, style)
            except:
                 pass
            self.deiconify()  # Show with frameless mode restored

    def toggle_maximize(self):
        if self.is_maximized:
            # Restore to previous size — animate
            self._animate_geometry(self.pre_max_geom)
            self.is_maximized = False
        else:
            self.pre_max_geom = self.geometry()
            # Get usable screen area (excludes taskbar)
            try:
                from ctypes import windll, Structure, c_long, byref
                class RECT(Structure):
                    _fields_ = [("left", c_long), ("top", c_long),
                                ("right", c_long), ("bottom", c_long)]
                rect = RECT()
                # SPI_GETWORKAREA = 0x0030
                windll.user32.SystemParametersInfoW(0x0030, 0, byref(rect), 0)
                x, y = rect.left, rect.top
                w = rect.right - rect.left
                h = rect.bottom - rect.top
            except Exception:
                x, y = 0, 0
                w = self.winfo_screenwidth()
                h = self.winfo_screenheight() - 40  # Rough taskbar estimate
            
            self._animate_geometry(f"{w}x{h}+{x}+{y}")
            self.is_maximized = True

    def _animate_geometry(self, target_geom):
        """Quick 4-step animated resize for smooth transitions."""
        # Parse current and target
        import re
        def parse_geom(g):
            m = re.match(r"(\d+)x(\d+)\+(-?\d+)\+(-?\d+)", g)
            if m:
                return [int(m.group(i)) for i in range(1, 5)]
            return None
        
        cur = parse_geom(self.geometry())
        tgt = parse_geom(target_geom)
        
        if not cur or not tgt:
            self.geometry(target_geom)
            return
        
        steps = 5
        for step in range(1, steps + 1):
            t = step / steps
            # Ease-out cubic
            t_ease = 1 - (1 - t) ** 3
            w = int(cur[0] + (tgt[0] - cur[0]) * t_ease)
            h = int(cur[1] + (tgt[1] - cur[1]) * t_ease)
            x = int(cur[2] + (tgt[2] - cur[2]) * t_ease)
            y = int(cur[3] + (tgt[3] - cur[3]) * t_ease)
            self.geometry(f"{w}x{h}+{x}+{y}")
            self.update_idletasks()

    def setup_ui(self):
        # 2. Main Content Area (Background) - Packed FIRST to be behind? 
        # Actually place is better for overlay.
        
        self.content_area = tk.Frame(self, bg=Colors.BACKGROUND)
        self.content_area.pack(fill="both", expand=True, padx=Metrics.PADDING_L, pady=Metrics.PADDING_L)
        
        # Container for Views
        self.view_container = tk.Frame(self.content_area, bg=Colors.BACKGROUND)
        self.view_container.pack(fill="both", expand=True)

        # 1. Integrated TitleBar (Nav + Controls) - Overlay on top
        self.top_frame = tk.Frame(self, bg=Colors.NAV_BG)
        self.top_frame.place(relx=0, rely=0, relwidth=1.0, height=30)
        
        self.navbar = IntegratedTitleBar(self.top_frame, items=["Home", "Sessions", "Analytics", "Settings"], 
                                  command_callback=self.show_view,
                                  window_control_callback=self.window_action, 
                                  height=30)
        self.navbar.pack(fill="both", expand=True)

        # Auto-Hide Logic
        self.in_focus_mode = False
        self.navbar_visible = True
        self.hide_timer = None
        self.last_mouse_y = 0
        self.check_navbar_hover()

    def check_navbar_hover(self):
        # Always show in Normal Mode
        if not self.in_focus_mode:
            if not self.navbar_visible:
                self.show_navbar()
            # Cancel any pending hide
            if self.hide_timer:
                self.after_cancel(self.hide_timer)
                self.hide_timer = None
            self.after(200, self.check_navbar_hover)
            return

        # Focus Mode: Auto-Hide Logic
        try:
            x, y = self.winfo_pointerxy()
            root_x = self.winfo_rootx()
            root_y = self.winfo_rooty()
            rel_y = y - root_y
            
            # Threshold to show: 50px from top
            if rel_y < 50 and 0 <= x - root_x <= self.winfo_width():
                 self.show_navbar()
            else:
                 # If mouse away, start hide timer logic
                 if self.navbar_visible and not self.hide_timer:
                     self.hide_timer = self.after(2000, self.hide_navbar)
        except:
            pass
        self.after(100, self.check_navbar_hover)

    def show_navbar(self):
        if self.hide_timer:
            self.after_cancel(self.hide_timer)
            self.hide_timer = None
            
        if not self.navbar_visible:
            self.top_frame.place(relx=0, rely=0, relwidth=1.0, height=30)
            self.navbar_visible = True

    def hide_navbar(self):
        if self.navbar_visible:
            # Check one last time if mouse is back at top
            try:
                _, y = self.winfo_pointerxy()
                if (y - self.winfo_rooty()) < 50:
                    self.hide_timer = None
                    return # Cancel hide
            except: pass

            self.top_frame.place_forget()
            self.navbar_visible = False
            self.hide_timer = None

    def show_view(self, view_name):
        # Save active session state before destroying the view
        self._save_active_session()
        
        # NORMAL MODE
        self.in_focus_mode = False
        self.show_navbar()
        # Add padding so navbar doesn't cover content
        self.content_area.pack_configure(padx=Metrics.PADDING_L, pady=(35, Metrics.PADDING_L))
        
        for widget in self.view_container.winfo_children():
            widget.destroy()
            
        if view_name == "Home":
            HomeView(self.view_container, self)
        elif view_name == "Sessions":
            BlocksView(self.view_container, self)
        elif view_name == "Analytics":
            AnalyticsView(self.view_container, self)
        elif view_name == "Settings":
            SettingsView(self.view_container, self)

    def _save_active_session(self):
        """Save the current Focus Mode session state before tab switch."""
        for widget in self.view_container.winfo_children():
            if isinstance(widget, ActiveRoutineView):
                # Cancel the timer to prevent orphan after callbacks
                if hasattr(widget, 'timer_id'):
                    widget.after_cancel(widget.timer_id)
                self.active_session = {
                    'index': widget.current_index,
                    'time_left': widget.time_left,
                    'is_paused': widget.is_paused,
                    'items': widget.items,
                }
                return

    def start_routine_flow(self):
        # FOCUS MODE
        self.in_focus_mode = True
        # Remove top padding for immersion (navbar will float over)
        self.content_area.pack_configure(padx=0, pady=0)
        
        for widget in self.view_container.winfo_children():
            widget.destroy()
        
        items = self.blocks_manager.get_items()
        
        # Restore saved session if available
        if self.active_session:
            saved = self.active_session
            self.active_session = None  # Clear so next start is fresh if they finish
            view = ActiveRoutineView(self.view_container, self, saved['items'], 
                                     resume_index=saved['index'],
                                     resume_time=saved['time_left'],
                                     resume_paused=saved['is_paused'])
        else:
            ActiveRoutineView(self.view_container, self, items)

    def enter_focus_mode(self):
        self.start_routine_flow()
        
    def reload_theme(self):
        # 1. Load Data
        from modules.theme_manager import ThemeManager
        _, t_data = ThemeManager.load_theme()
        
        # 2. Update Static Colors
        Colors.update(t_data)
        
        # 3. Update Root Styles
        self.configure(bg=Colors.BACKGROUND)
        self.content_area.configure(bg=Colors.BACKGROUND)
        self.view_container.configure(bg=Colors.BACKGROUND)
        
        # 4. Refresh TitleBar
        # The easiest way is to re-create it or just update its background
        # Since NavBar has internal colors, recreation is cleaner
        self.navbar.destroy()
        self.navbar = IntegratedTitleBar(self.top_frame, items=["Home", "Sessions", "Analytics", "Settings"], 
                                  command_callback=self.show_view,
                                  window_control_callback=self.window_action, 
                                  height=30)
        self.navbar.pack(fill="both", expand=True)
        self.top_frame.configure(bg=Colors.NAV_BG)
        
        # 5. Reload Current View (Settings)
        # Note: We assume we are in Settings if changing theme
        self.show_view("Settings")
