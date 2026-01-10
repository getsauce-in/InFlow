import tkinter as tk
from tkinter import simpledialog
import threading
from theme import Colors
from ui.views.base import BaseView
from ui.components.edit_modal import EditModal
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
        
        # TEMPLATE BTN
        self.btn_tmpl = tk.Label(self.wrapper, text="Load Template ▾", font=("Segoe UI", 10), 
                                 bg=Colors.SURFACE_1, fg=Colors.TEXT_SECONDARY, padx=15, pady=5)
        self.btn_tmpl.pack(anchor="nw", pady=(0, 40))
        self.btn_tmpl.bind("<Button-1>", self.show_templates)
        self.btn_tmpl.bind("<Enter>", lambda e: self.btn_tmpl.config(cursor="hand2", bg=Colors.SURFACE_2))
        self.btn_tmpl.bind("<Leave>", lambda e: self.btn_tmpl.config(bg=Colors.SURFACE_1))


        # BLOCKS LIST
        self.list_view = BlocksList(self.wrapper, self.app, width=600)
        self.list_view.pack()
        self.list_view.set_callbacks(self.show_edit_modal)
        
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

    def update_header(self):
        self.lbl_title.config(text=self.blocks_manager.routine_name)

    def add_block(self, e):
        self.blocks_manager.add_item("New Block", 15, "🟦")
        self.list_view.refresh()
        self.on_resize(None) # Recalc scroll

    def show_edit_modal(self, item):
        
        def save_cb(id, title, duration, icon):
            try: d = int(duration)
            except: d = item.duration
            if d < 1: d = 1
            
            # --- ROBUST OPTIMISTIC UPDATE ---
            # Update the Single Source of Truth immediately
            self.blocks_manager.update_item_optimistic(id, title.strip(), d, icon)
            
            # Refresh UI from that Source
            self.list_view.refresh()
            self.list_view.update_idletasks() # Force Immediate Redraw
            
            # --- THREADED PERSISTENCE ---
            def _threaded_persist():
                self.blocks_manager.update_item(id, title.strip(), d, icon)
                # No need to sync UI again usually, but good for consistency check
                self.after(0, lambda: self.list_view.refresh())

            threading.Thread(target=_threaded_persist, daemon=True).start()
            
        def del_cb(id):
            # Optimistic Remove
            self.blocks_manager.items = [i for i in self.blocks_manager.items if i.id != id]
            self.list_view.refresh()
            self.on_resize(None)

            # Threaded Persistence
            def _threaded_persist():
                self.blocks_manager.delete_item(id)
                self.after(0, lambda: self.list_view.refresh())
            
            threading.Thread(target=_threaded_persist, daemon=True).start()
            
        def cancel_cb():
            pass

        modal = EditModal(self.app, item, save_cb, del_cb, cancel_cb)
        
        # Inject icon cycler logic if needed, or move to EditModal entirely
        def cycle_icon(e):
            curr = modal.lbl_icon.cget("text")
            nxt = self.blocks_manager.get_next_icon(curr)
            modal.lbl_icon.config(text=nxt)
        modal.lbl_icon.bind("<Button-1>", cycle_icon)

        modal.lift()

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
        self.on_resize(None)
