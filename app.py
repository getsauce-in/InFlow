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
from active_view import ActiveRoutineView
import database

class Flow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("InFlow")
        
        # Frameless Window
        self.overrideredirect(True) 
        self.title_bar_height = 30
        
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
        
        self.setup_ui()
        self.show_view("Sessions") 
        # Reverting default to Home or Routine? User asked for Routine page design heavily. 
        # But V2 usually defaults to Home. I'll keep Routine to verify the revert.

    def window_action(self, action):
        if action == "close":
            self.destroy()
        elif action == "minimize":
            self.overrideredirect(False)
            self.update_idletasks()
            self.iconify()
            self.bind("<Map>", self.on_restore_from_minimize)
        elif action == "maximize":
            self.toggle_maximize()

    def on_restore_from_minimize(self, event):
        if self.state() == "normal":
            self.overrideredirect(True)
            self.unbind("<Map>")
            try:
                 hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
                 style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
                 style |= 0x00040000
                 ctypes.windll.user32.SetWindowLongW(hwnd, -20, style)
            except:
                 pass

    def toggle_maximize(self):
        if self.is_maximized:
            self.geometry(self.pre_max_geom)
            self.is_maximized = False
        else:
            self.pre_max_geom = self.geometry()
            screen_w = self.winfo_screenwidth()
            screen_h = self.winfo_screenheight()
            self.geometry(f"{screen_w}x{screen_h}+0+0")
            self.is_maximized = True
            
        self.update_idletasks()
        self.update_idletasks()

    def setup_ui(self):
        # 2. Main Content Area (Background) - Packed FIRST to be behind? 
        # Actually place is better for overlay.
        
        self.content_area = tk.Frame(self, bg=Colors.BACKGROUND)
        self.content_area.pack(fill="both", expand=True, padx=Metrics.PADDING_L, pady=Metrics.PADDING_L)
        
        # Container for Views
        self.view_container = tk.Frame(self.content_area, bg=Colors.BACKGROUND)
        self.view_container.pack(fill="both", expand=True)

        # 1. Integrated Title Bar (Nav + Controls) - Overlay on top
        self.top_frame = tk.Frame(self, bg=Colors.NAV_BG)
        self.top_frame.place(relx=0, rely=0, relwidth=1.0, height=30)
        
        self.navbar = IntegratedTitleBar(self.top_frame, items=["Home", "Sessions", "Settings"], 
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
        elif view_name == "Settings":
            SettingsView(self.view_container, self)

    def start_routine_flow(self):
        # FOCUS MODE
        self.in_focus_mode = True
        # Remove top padding for immersion (navbar will float over)
        self.content_area.pack_configure(padx=0, pady=0)
        
        for widget in self.view_container.winfo_children():
            widget.destroy()
        items = self.blocks_manager.get_items()
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
        self.navbar = IntegratedTitleBar(self.top_frame, items=["Home", "Sessions", "Settings"], 
                                  command_callback=self.show_view,
                                  window_control_callback=self.window_action, 
                                  height=30)
        self.navbar.pack(fill="both", expand=True)
        self.top_frame.configure(bg=Colors.NAV_BG)
        
        # 5. Reload Current View (Settings)
        # Note: We assume we are in Settings if changing theme
        self.show_view("Settings")
