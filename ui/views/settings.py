import tkinter as tk
from tkinter import messagebox
from theme import Colors, Fonts, CURRENT_THEME, Metrics
from ui.views.base import BaseView
from modules.theme_manager import ThemeManager
from ui_components import SettingsGroup, RoundedRect

class SettingsView(BaseView):
    def __init__(self, master, app_context):
        super().__init__(master, app_context)
        self.app_context = app_context # Redundant fallback for safety
        self.configure(bg=Colors.BACKGROUND)
        
        # --- SCROLLABLE CONTAINER ---
        container = tk.Canvas(self, bg=Colors.BACKGROUND, highlightthickness=0)
        container.pack(fill="both", expand=True)
        
        # 1. Define Content Frame FIRST
        content = tk.Frame(container, bg=Colors.BACKGROUND)
        
        # 2. Create Window using the Frame
        # Initialize with current app width to prevent "jump" from left to center
        initial_w = self.app.winfo_width()
        self.list_window = container.create_window((0, 0), window=content, anchor="nw", width=initial_w)
        
        # Center Content Wrapper (limit width to max 700 for readability)
        # expand=True implies centering in the available space if fill is not both
        wrapper = tk.Frame(content, bg=Colors.BACKGROUND)
        wrapper.pack(pady=40, padx=20, expand=True) 
        
        # --- 1. HEADER ---
        tk.Label(wrapper, text="Settings", font=("Segoe UI", 26, "bold"), 
                 bg=Colors.BACKGROUND, fg=Colors.TEXT_PRIMARY).pack(anchor="w", pady=(0, 20))
        
        # --- 2. APPEARANCE (THEMES) ---
        self.create_section_label(wrapper, "APPEARANCE")
        
        self.theme_grid = tk.Frame(wrapper, bg=Colors.BACKGROUND)
        self.theme_grid.pack(fill="x", pady=(0, 20))
        self.render_themes()
        
        # Status Label (Hidden default)
        self.lbl_status = tk.Label(wrapper, text="", font=Fonts.BODY, bg=Colors.BACKGROUND, fg=Colors.ACCENT)
        self.lbl_status.pack(pady=(0, 20))
        
        # Current info
        curr_theme, _ = ThemeManager.load_theme()
        tk.Label(wrapper, text=f"Active Theme: {curr_theme}", font=Fonts.CAPTION, 
                 bg=Colors.BACKGROUND, fg=Colors.TEXT_SECONDARY).pack(pady=5)

        # --- 3. GENERAL ---
        from tkinter import messagebox
        def show_msg(title, msg):
             messagebox.showinfo(title, msg)

        gen_rows = [
            ("General", "", lambda: show_msg("General", "General settings placeholder.")),
            ("Notifications", "On", lambda: show_msg("Notifications", "Notifications are currently ON.")),
            ("Software Update", "v1.0.2", lambda: show_msg("Update", "You are on the latest version."))
        ]
        SettingsGroup(wrapper, rows=gen_rows, title="GENERAL", width=600).pack(pady=(0, 20))

        # --- 4. DATA ---
        def reset_app():
            if messagebox.askyesno("Reset", "Load default 'Morning' template and reset session data?"):
                self.app.blocks_manager.load_template("Morning")
                messagebox.showinfo("Reset", "Default template loaded.")

        data_rows = [
            ("Reset to Standard Template", "Morning", reset_app)
        ]
        SettingsGroup(wrapper, rows=data_rows, title="DATA", width=600).pack(pady=(0, 20))

        # --- 5. PRIVACY & LEGAL ---
        legal_rows = [
            ("Privacy Policy", "", lambda: show_msg("Privacy", "Your data is stored locally.\nWe respect your privacy.")),
            ("Terms of Service", "", lambda: show_msg("Terms", "Standard Terms of Service apply.")),
            ("Licenses", "", lambda: show_msg("Licenses", "MIT License\nCopyright (c) 2026 InFlow"))
        ]
        SettingsGroup(wrapper, rows=legal_rows, title="LEGAL", width=600).pack(pady=(0, 20))

        # Footer
        tk.Label(wrapper, text="InFlow v1.0.2\nMade with <3", font=Fonts.CAPTION, 
                 bg=Colors.BACKGROUND, fg=Colors.TEXT_TERTIARY, justify="center").pack(pady=20)

        # Update scroll region
        content.update_idletasks()
        container.configure(scrollregion=container.bbox("all"))
        
        # Responsive Layout Logic
        def on_resize(event):
            # Update the width of the canvas window to match the canvas
            # This forces the 'content' frame to fill the screen width
            # The 'wrapper' inside it will then stay centered due to pack(expand=True)
            container.itemconfig(self.list_window, width=event.width)
                 
        container.bind("<Configure>", on_resize)
        
        # Mousewheel - Only active when hovering container
        def on_mousewheel(event):
            container.yview_scroll(int(-1*(event.delta/120)), "units")
            
        def bind_scroll(e):
            container.bind_all("<MouseWheel>", on_mousewheel)
        def unbind_scroll(e):
            container.unbind_all("<MouseWheel>")
            
        container.bind("<Enter>", bind_scroll)
        container.bind("<Leave>", unbind_scroll)

    def create_section_label(self, parent, text):
        tk.Label(parent, text=text, font=("Segoe UI", 9, "bold"), fg=Colors.TEXT_SECONDARY, 
                 bg=Colors.BACKGROUND).pack(anchor="w", padx=10, pady=(10, 5))

    # Profile Card Removed per user request

    def render_themes(self):
        themes = ThemeManager.get_all_themes()
        curr_theme, _ = ThemeManager.load_theme()
        
        r, c = 0, 0
        for name, data in themes.items():
            self.create_theme_card(self.theme_grid, name, data, r, c, curr_theme)
            c += 1
            if c > 2:
                c = 0; r += 1

    def create_theme_card(self, parent, name, data, r, c, curr_theme):
        # Card
        is_active = (name == curr_theme)
        bg = data["BACKGROUND"]
        accent = data["ACCENT"]
        
        # Slightly larger cards for this layout
        card = tk.Canvas(parent, width=180, height=100, bg=Colors.BACKGROUND, highlightthickness=0, cursor="hand2")
        card.grid(row=r, column=c, padx=5, pady=5)
        
        # Draw Preview - Rounded
        RoundedRect.draw(card, 5, 5, 175, 95, 12, bg, outline=Colors.SURFACE_3)
        
        # Accent Strip
        RoundedRect.draw(card, 5, 65, 175, 95, 12, data["SURFACE_1"]) 
        # Fix rounded corners consistency? Actually simpler rect for bottom part usually
        # Just drawing a circle for accent
        card.create_oval(145, 15, 165, 35, fill=accent, outline="")
        
        # Text
        text_col = data["TEXT_PRIMARY"]
        card.create_text(20, 80, text=name, fill=text_col, font=("Segoe UI", 10, "bold"), anchor="w")
        
        # Selection Border
        if is_active:
             RoundedRect.draw(card, 2, 2, 178, 98, 14, "", outline=Colors.ACCENT, width=2)
             
        card.bind("<Button-1>", lambda e: self.apply_theme(name))
        
    def apply_theme(self, name):
        if name == CURRENT_THEME: return
        ThemeManager.save_theme(name)
        # Hot Reload!
        self.app.reload_theme()
