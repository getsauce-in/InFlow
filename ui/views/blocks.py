import tkinter as tk
from tkinter import simpledialog
import threading
from theme import Colors
from ui.views.base import BaseView
from ui.components.blocks_list import BlocksList
from modules import templates

class BlocksView(BaseView):
    def __init__(self, master, app_context):
        super().__init__(master, app_context)
        self.app = app_context
        self.blocks_manager = self.app.blocks_manager
        
        self.setup_layout()
        self.update_header()
        
    def setup_layout(self):
        self.configure(bg=Colors.BACKGROUND)
        
        # 1. Scrollable Container
        self.container = tk.Canvas(self, bg=Colors.BACKGROUND, highlightthickness=0)
        self.container.pack(fill="both", expand=True)
        
        # 2. Content Frame
        self.content = tk.Frame(self.container, bg=Colors.BACKGROUND)
        self.content_window = self.container.create_window((0,0), window=self.content, anchor="nw")
        
        # 3. Wrapper (Centered)
        self.wrapper = tk.Frame(self.content, bg=Colors.BACKGROUND)
        self.wrapper.pack(pady=40, expand=True)
        
        # --- UI ELEMENTS in Wrapper ---
        
        # HEADER
        self.lbl_title = tk.Label(self.wrapper, text=self.blocks_manager.routine_name, 
                                  font=("Segoe UI", 26, "bold"), bg=Colors.BACKGROUND, fg=Colors.TEXT_PRIMARY)
        self.lbl_title.pack(anchor="nw", pady=(0, 20))
        self.lbl_title.bind("<Button-1>", self.edit_routine_name)
        self.lbl_title.bind("<Enter>", lambda e: self.lbl_title.config(cursor="hand2"))
        
        # HEADERS FRAME
        header_actions = tk.Frame(self.wrapper, bg=Colors.BACKGROUND)
        header_actions.pack(anchor="nw", pady=(0, 40))
        
        # TEMPLATE BTN
        self.btn_tmpl = tk.Label(header_actions, text="Load Template ▾", font=("Segoe UI", 10), 
                                 bg=Colors.SURFACE_1, fg=Colors.TEXT_SECONDARY, padx=15, pady=5)
        self.btn_tmpl.pack(side="left", padx=(0, 10))
        self.btn_tmpl.bind("<Button-1>", self.show_templates)
        self.btn_tmpl.bind("<Enter>", lambda e: self.btn_tmpl.config(cursor="hand2", bg=Colors.SURFACE_2))
        self.btn_tmpl.bind("<Leave>", lambda e: self.btn_tmpl.config(bg=Colors.SURFACE_1))

        # DAY BTN
        self.btn_day = tk.Label(header_actions, text="Load 30-Day Path ▾", font=("Segoe UI", 10, "bold"), 
                                bg=Colors.SURFACE_1, fg=Colors.NEON_YELLOW, padx=15, pady=5)
        self.btn_day.pack(side="left")
        self.btn_day.bind("<Button-1>", self.show_curriculum)
        self.btn_day.bind("<Enter>", lambda e: self.btn_day.config(cursor="hand2", bg=Colors.SURFACE_2))
        self.btn_day.bind("<Leave>", lambda e: self.btn_day.config(bg=Colors.SURFACE_1))


        # STATS BAR
        self.stats_frame = tk.Frame(self.wrapper, bg=Colors.BACKGROUND)
        self.stats_frame.pack(anchor="nw", fill="x", pady=(0, 32))
        
        self.lbl_stat_blocks = self.create_stat(self.stats_frame, "0", "Blocks", first=True)
        self.create_divider(self.stats_frame)
        self.lbl_stat_time = self.create_stat(self.stats_frame, "0h", "Total Time")
        self.create_divider(self.stats_frame)
        self.lbl_stat_python = self.create_stat(self.stats_frame, "0h", "Python")
        self.create_divider(self.stats_frame)
        self.lbl_stat_realhow = self.create_stat(self.stats_frame, "0h", "RealHow")
        self.create_divider(self.stats_frame)
        self.lbl_stat_flagged = self.create_stat(self.stats_frame, "0", "Flagged")

        # BLOCKS LIST
        self.list_view = BlocksList(self.wrapper, self.app, width=800)
        self.list_view.pack()
        
        # ADD BUTTON
        tk.Label(self.wrapper, text="+ Add Session Block", font=("Segoe UI", 11), 
                 fg=Colors.TEXT_SECONDARY, bg=Colors.BACKGROUND, cursor="hand2").pack(pady=30)
        btn_add = self.wrapper.winfo_children()[-1]
        btn_add.bind("<Button-1>", self.add_block)
        
        # --- RESIZE LOGIC ---
        self.bind("<Configure>", self.on_resize)
        self.container.bind("<Configure>", lambda e: self.container.itemconfig(self.content_window, width=e.width))
        
        # Scroll Bindings
        def _on_mousewheel(event):
            self.container.yview_scroll(int(-1*(event.delta/120)), "units")
        self.bind_all("<MouseWheel>", _on_mousewheel)
        self.bind("<Destroy>", lambda e: self.unbind_all("<MouseWheel>"))

    def on_resize(self, event):
        # Update scroll region
        self.content.update_idletasks()
        self.container.config(scrollregion=self.container.bbox("all"))

    def create_stat(self, parent, val, label, first=False):
        f = tk.Frame(parent, bg=Colors.BACKGROUND)
        f.pack(side="left", padx=(0, 24) if first else 24)
        num_lbl = tk.Label(f, text=val, font=("Consolas", 20, "bold"), fg=Colors.NEON_YELLOW, bg=Colors.BACKGROUND)
        num_lbl.pack()
        tk.Label(f, text=label.upper(), font=("Segoe UI", 9, "bold"), fg=Colors.TEXT_TERTIARY, bg=Colors.BACKGROUND).pack(pady=(2,0))
        return num_lbl
        
    def create_divider(self, parent):
        tk.Frame(parent, width=1, bg=Colors.SURFACE_3).pack(side="left", fill="y", pady=5)

    def update_header(self):
        self.lbl_title.config(text=self.blocks_manager.routine_name)
        self.update_stats()
        
    def update_stats(self):
        items = self.blocks_manager.items
        total_m = sum(i.duration for i in items)
        self.lbl_stat_blocks.config(text=str(len(items)))
        
        def fmt(m):
            h = m / 60
            if h.is_integer(): return f"{int(h)}h"
            return f"{h:.2g}h"
            
        self.lbl_stat_time.config(text=fmt(total_m))
        
        py_m = 0
        rh_m = 0
        flagged = 0
        for i in items:
            title = i.title.lower()
            if "python" in title: py_m += i.duration
            if "realhow" in title or "dist" in title or "x" in title or "reddit" in title: rh_m += i.duration
            if "review" in title or "write" in title: flagged += 1
            
        self.lbl_stat_python.config(text=fmt(py_m))
        self.lbl_stat_realhow.config(text=fmt(rh_m))
        self.lbl_stat_flagged.config(text=str(flagged))

    def add_block(self, e):
        self.blocks_manager.add_item("New Block", 15, "🟦")
        self.list_view.refresh()
        self.on_resize(None) # Recalc scroll

    def edit_routine_name(self, e):
        new_name = simpledialog.askstring("Routine Name", "Enter routine name:", initialvalue=self.blocks_manager.routine_name)
        if new_name:
            self.blocks_manager.set_routine_name(new_name)
            self.update_header()

    def show_templates(self, e):
        menu = tk.Menu(self, tearoff=0)
        for t in templates.TEMPLATES:
            menu.add_command(label=t, command=lambda x=t: self.load_template(x))
        menu.tk_popup(e.x_root, e.y_root)
        
    def load_template(self, t):
        self.blocks_manager.load_template(t)
        self.update_header()
        self.list_view.refresh()
        self.update_stats()
        self.on_resize(None)
        
    def show_curriculum(self, e):
        import json
        import os
        filepath = os.path.join("assets", "curriculum.json")
        if not os.path.exists(filepath): return
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        menu = tk.Menu(self, tearoff=0)
        # Menus scroll automatically in Tkinter 8.6
        for day in list(data.keys()):
            menu.add_command(label=day, command=lambda d=day: self.load_curriculum(d))
            
        menu.tk_popup(e.x_root, e.y_root)
        
    def load_curriculum(self, day):
        self.blocks_manager.load_curriculum_day(day)
        self.update_header()
        self.list_view.refresh()
        self.update_stats()
        self.on_resize(None)
