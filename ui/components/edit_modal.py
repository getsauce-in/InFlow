import tkinter as tk
from tkinter import messagebox
from theme import Colors

class EditModal(tk.Frame):
    def __init__(self, master, item, on_save, on_delete, on_cancel):
        super().__init__(master, bg=Colors.BACKGROUND)
        self.item = item
        self.on_save = on_save
        self.on_delete = on_delete
        self.on_cancel = on_cancel
        self.edit_icon = item.icon
        
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # 1. Overlay (Dim Background)
        self.overlay = tk.Frame(self, bg="#000000")
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.overlay.bind("<Button-1>", lambda e: self.close())
        try: self.overlay.configure(bg="#00000099") 
        except: pass 
        self.overlay.configure(bg="#1e1e1e") # Dark mode fallback
        
        # 2. Modal Card
        self.card = tk.Frame(self, bg=Colors.SURFACE_1, bd=0, highlightthickness=1, highlightbackground=Colors.SURFACE_3)
        self.card.place(relx=0.5, rely=0.5, anchor="center", width=500, height=300)
        
        # 3. Content
        # Header
        tk.Label(self.card, text="Edit Session Block", font=("Segoe UI", 16, "bold"), 
                 bg=Colors.SURFACE_1, fg=Colors.TEXT_PRIMARY).pack(pady=(25, 15))
        
        # Form Container
        form = tk.Frame(self.card, bg=Colors.SURFACE_1)
        form.pack(fill="x", padx=40)
        
        # Icon & Title Row
        row1 = tk.Frame(form, bg=Colors.SURFACE_1)
        row1.pack(fill="x", pady=10)
        
        # Icon
        self.lbl_icon = tk.Label(row1, text=self.edit_icon, font=("Segoe UI Emoji", 24), 
                                 bg=Colors.SURFACE_1, fg=Colors.ACCENT, cursor="hand2")
        self.lbl_icon.pack(side="left", padx=(0, 15))
        
        # Title
        self.var_title = tk.StringVar(value=item.title)
        ent_title = tk.Entry(row1, textvariable=self.var_title, font=("Segoe UI", 14), 
                             bg=Colors.SURFACE_2, fg=Colors.TEXT_PRIMARY, relief="flat", insertbackground=Colors.ACCENT)
        ent_title.pack(side="left", fill="x", expand=True, ipady=5)
        ent_title.bind("<Return>", lambda e: self.save())
        ent_title.select_range(0, tk.END)
        ent_title.focus_set()
        
        # Duration Row
        row2 = tk.Frame(form, bg=Colors.SURFACE_1)
        row2.pack(fill="x", pady=10)
        
        tk.Label(row2, text="Duration (min)", font=("Segoe UI", 10), 
                 bg=Colors.SURFACE_1, fg=Colors.TEXT_SECONDARY).pack(side="left")
        
        self.var_dur = tk.StringVar(value=str(item.duration))
        ent_dur = tk.Entry(row2, textvariable=self.var_dur, font=("Segoe UI", 12), width=10,
                           bg=Colors.SURFACE_2, fg=Colors.TEXT_PRIMARY, relief="flat", justify="center")
        ent_dur.pack(side="right", ipady=3)
        ent_dur.bind("<Return>", lambda e: self.save())

        # Buttons
        btn_box = tk.Frame(self.card, bg=Colors.SURFACE_1)
        btn_box.pack(fill="x", pady=30, padx=40)
        
        # Delete (Left)
        del_btn = tk.Label(btn_box, text="Delete Block", font=("Segoe UI", 10), 
                           bg=Colors.SURFACE_1, fg="#E81123", cursor="hand2")
        del_btn.pack(side="left")
        del_btn.bind("<Button-1>", lambda e: self.delete())
        
        # Save (Right)
        save_btn = tk.Label(btn_box, text="Done", font=("Segoe UI", 10, "bold"), 
                            bg=Colors.ACCENT, fg="#000000", padx=20, pady=8, cursor="hand2")
        save_btn.pack(side="right")
        save_btn.bind("<Button-1>", lambda e: self.save())
        
    def toggle_icon(self, e):
        pass
        
    def save(self):
        t = self.var_title.get()
        d = self.var_dur.get()
        self.on_save(self.item.id, t, d, self.lbl_icon.cget("text"))
        self.close()

    def delete(self):
        if messagebox.askyesno("Delete", "Delete this block?"):
            self.on_delete(self.item.id)
            self.close()

    def close(self):
        self.destroy()
        self.on_cancel()
