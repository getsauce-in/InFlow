import tkinter as tk
from tkinter import messagebox
from theme import Colors, Fonts, CURRENT_THEME, Metrics
from ui.views.base import BaseView
from modules.theme_manager import ThemeManager
from ui_components import SettingsGroup, RoundedRect
from modules.sync_manager import sync_to_cloud, sync_from_cloud

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
        self.wrapper = tk.Frame(content, bg=Colors.BACKGROUND)
        self.wrapper.pack(pady=40, expand=True)
        
        # --- 1. HEADER ---
        tk.Label(self.wrapper, text="Settings", font=("Segoe UI", 26, "bold"), 
                 bg=Colors.BACKGROUND, fg=Colors.TEXT_PRIMARY).pack(anchor="w", pady=(0, 20))
        
        # --- 2. APPEARANCE (THEMES) ---
        self.create_section_label(self.wrapper, "APPEARANCE")
        
        self.theme_grid = tk.Frame(self.wrapper, bg=Colors.BACKGROUND)
        self.theme_grid.pack(fill="x", pady=(0, 20))
        self.render_themes()
        
        # Status Label (Hidden default)
        self.lbl_status = tk.Label(self.wrapper, text="", font=Fonts.BODY, bg=Colors.BACKGROUND, fg=Colors.ACCENT)
        self.lbl_status.pack(pady=(0, 20))
        
        # Current info
        curr_theme, _ = ThemeManager.load_theme()
        tk.Label(self.wrapper, text=f"Active Theme: {curr_theme}", font=Fonts.CAPTION, 
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
        SettingsGroup(self.wrapper, rows=gen_rows, title="GENERAL", width=600).pack(pady=(0, 20))

        # --- SYNC ---
        def run_sync_push():
            try:
                self.lbl_status.config(text="Syncing to cloud...")
                self.update_idletasks()
                sync_to_cloud()
                self.lbl_status.config(text="Sync to cloud complete!")
                messagebox.showinfo("Sync Successful", "Your data has been pushed to the cloud.")
            except Exception as e:
                self.lbl_status.config(text="Sync failed.")
                messagebox.showerror("Sync Error", f"Failed to sync to cloud:\n{str(e)}")

        def run_sync_pull():
            try:
                self.lbl_status.config(text="Pulling from cloud...")
                self.update_idletasks()
                sync_from_cloud()
                self.lbl_status.config(text="Pull from cloud complete!")
                # Force refresh data by reloading current view or showing message
                messagebox.showinfo("Sync Successful", "Data pulled successfully. Restarting app/view to reflect changes.")
                self.app.show_view("Settings") # easiest way to reload
            except Exception as e:
                self.lbl_status.config(text="Sync failed.")
                messagebox.showerror("Sync Error", f"Failed to pull from cloud:\n{str(e)}")

        sync_rows = [
            ("Push local data to Cloud", "", run_sync_push),
            ("Pull Cloud data to local", "", run_sync_pull)
        ]
        SettingsGroup(self.wrapper, rows=sync_rows, title="CLOUD SYNC (Supabase)", width=600).pack(pady=(0, 20))

        # --- 4. DATA ---
        def reset_app():
            if messagebox.askyesno("Reset", "Load default 'Morning' template and reset session data?"):
                self.app.blocks_manager.load_template("Morning")
                messagebox.showinfo("Reset", "Default template loaded.")

        data_rows = [
            ("Reset to Standard Template", "Morning", reset_app)
        ]
        SettingsGroup(self.wrapper, rows=data_rows, title="DATA", width=600).pack(pady=(0, 20))

        # --- 5. PRIVACY & LEGAL ---
        legal_rows = [
            ("Privacy Policy", "", lambda: show_msg("Privacy", "Your data is stored locally.\nWe respect your privacy.")),
            ("Terms of Service", "", lambda: show_msg("Terms", "Standard Terms of Service apply.")),
            ("Licenses", "", lambda: show_msg("Licenses", "MIT License\nCopyright (c) 2026 InFlow"))
        ]
        SettingsGroup(self.wrapper, rows=legal_rows, title="LEGAL", width=600).pack(pady=(0, 20))

        # Footer
        tk.Label(self.wrapper, text="InFlow v1.0.2\nMade with <3", font=Fonts.CAPTION, 
                 bg=Colors.BACKGROUND, fg=Colors.TEXT_TERTIARY, justify="center").pack(pady=20)

        # Update scroll region
        content.update_idletasks()
        container.configure(scrollregion=container.bbox("all"))
        
        # Responsive Layout Logic
        def on_resize(event):
            container.itemconfig(self.list_window, width=event.width)
            content.update_idletasks()
            container.config(scrollregion=container.bbox("all"))
                 
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
        pad_r = 30 if c < 2 else 0
        card.grid(row=r, column=c, padx=(0, pad_r), pady=(0, 20))
        
        # Draw Preview - Rounded
        RoundedRect.draw(card, 0, 0, 180, 100, 12, bg, outline=Colors.SURFACE_3)
        
        # Accent Strip
        RoundedRect.draw(card, 0, 60, 180, 40, 12, data["SURFACE_1"]) 
        # Fix rounded corners consistency? Actually simpler rect for bottom part usually
        # Just drawing a circle for accent
        card.create_oval(140, 15, 160, 35, fill=accent, outline="")
        
        # Text
        text_col = data["TEXT_PRIMARY"]
        card.create_text(15, 75, text=name, fill=text_col, font=("Segoe UI", 10, "bold"), anchor="w")
        
        # Selection Border
        if is_active:
             RoundedRect.draw(card, 0, 0, 180, 100, 14, "", outline=Colors.ACCENT, width=2)
             
        card.bind("<Button-1>", lambda e: self.apply_theme(name))
        
    def apply_theme(self, name):
        if name == CURRENT_THEME: return
        ThemeManager.save_theme(name)
        # Hot Reload!
        self.app.reload_theme()
