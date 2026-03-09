import tkinter as tk
from tkinter import messagebox
from theme import Colors, Metrics, Fonts
from ui_components import RoundedRect

class EditModal(tk.Frame):
    def __init__(self, master, item, on_save, on_delete, on_cancel):
        super().__init__(master, bg=Colors.BACKGROUND)
        self.item = item
        self.on_save = on_save
        self.on_delete = on_delete
        self.on_cancel = on_cancel
        self.edit_icon = item.icon
        
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.bind_all("<Escape>", lambda e: self.close())
        
        # 1. Overlay (Dim Background)
        self.overlay = tk.Frame(self, bg="#000")
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.overlay.bind("<Button-1>", lambda e: self.close())
        try: self.overlay.configure(bg="#000000aa") 
        except: pass 
        
        # 2. Main Card
        self.card = tk.Canvas(self, bg="#141414", highlightthickness=0, width=400, height=450)
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        RoundedRect.draw(self.card, 0, 0, 400, 450, 22, "#141414", border_color="rgba(255,255,255,0.08)", border_width=1)
        
        # Prevent clicks on the card from bubbling to overlay
        self.card.bind("<Button-1>", lambda e: "break")
        
        # --- HEADER ---
        self.card.create_text(26, 36, text="Edit Block", font=("Segoe UI", 15, "bold"), fill="#f0f0f0", anchor="w")
        btn_close = tk.Label(self.card, text="✕", font=("Segoe UI", 12), bg="#141414", fg="#888", cursor="hand2")
        btn_close.place(x=350, y=24, width=28, height=28)
        btn_close.bind("<Button-1>", lambda e: self.close())
        btn_close.bind("<Enter>", lambda e: btn_close.config(fg="#f0f0f0"))
        btn_close.bind("<Leave>", lambda e: btn_close.config(fg="#888"))

        # --- NAME FIELD ---
        RoundedRect.draw(self.card, 26, 70, 374, 120, 14, "#1a1a1a", border_color="rgba(255,255,255,0.05)")
        self.lbl_icon = tk.Label(self.card, text=self.edit_icon, font=("Segoe UI Emoji", 17), bg="#1a1a1a", cursor="hand2")
        self.lbl_icon.place(x=40, y=82)
        
        # Strip time prefixes from title for editing
        clean_title = self.item.title
        t_str = ""
        if " • " in clean_title:
            t_str, clean_title = clean_title.split(" • ", 1)
            
        self.var_title = tk.StringVar(value=clean_title)
        ent_title = tk.Entry(self.card, textvariable=self.var_title, font=("Segoe UI", 15, "bold"), 
                             bg="#1a1a1a", fg="#f0f0f0", relief="flat", insertbackground=Colors.NEON_YELLOW)
        ent_title.place(x=76, y=83, width=280)
        ent_title.bind("<Return>", lambda e: self.save())
        ent_title.focus_set()

        # --- TIME PARSER ---
        self.var_start = tk.StringVar(value="--:--")
        self.var_start_pm = tk.StringVar(value="AM")
        self.var_end = tk.StringVar(value="--:--")
        self.var_end_pm = tk.StringVar(value="PM")
        
        if t_str:
            t_start, *t_end = t_str.split("-") if "-" in t_str else t_str.split("–")
            if t_start:
                s = t_start.strip().split(" ")
                self.var_start.set(s[0])
                if len(s) > 1: self.var_start_pm.set(s[1])
            if t_end:
                e = t_end[0].strip().split(" ")
                self.var_end.set(e[0])
                if len(e) > 1: self.var_end_pm.set(e[1])
        else:
            self.var_start.set("00:00")
            self.var_end.set("00:00")

        # --- TIME GRID ---
        RoundedRect.draw(self.card, 26, 134, 196, 214, 14, "#1a1a1a", border_color="rgba(255,255,255,0.05)")
        RoundedRect.draw(self.card, 204, 134, 374, 214, 14, "#1a1a1a", border_color="rgba(255,255,255,0.05)")
        
        self.card.create_text(42, 154, text="START", font=("Segoe UI", 10, "bold"), fill="#444", anchor="w")
        
        ent_s = tk.Entry(self.card, textvariable=self.var_start, font=("Consolas", 26, "bold"), width=5, bg="#1a1a1a", fg="#f0f0f0", relief="flat", insertbackground="#f0f0f0")
        ent_s.place(x=38, y=164)
        ent_s.bind("<KeyRelease>", self.update_math)
        
        ent_s_pm = tk.Entry(self.card, textvariable=self.var_start_pm, font=("Segoe UI", 12, "bold"), width=3, bg="#1a1a1a", fg="#888", relief="flat", insertbackground="#888")
        ent_s_pm.place(x=144, y=177)
        ent_s_pm.bind("<KeyRelease>", self.update_math)
        
        self.card.create_text(220, 154, text="END", font=("Segoe UI", 10, "bold"), fill="#444", anchor="w")
        
        ent_e = tk.Entry(self.card, textvariable=self.var_end, font=("Consolas", 26, "bold"), width=5, bg="#1a1a1a", fg="#f0f0f0", relief="flat", insertbackground="#f0f0f0")
        ent_e.place(x=216, y=164)
        ent_e.bind("<KeyRelease>", self.update_math)
        
        ent_e_pm = tk.Entry(self.card, textvariable=self.var_end_pm, font=("Segoe UI", 12, "bold"), width=3, bg="#1a1a1a", fg="#888", relief="flat", insertbackground="#888")
        ent_e_pm.place(x=324, y=177)
        ent_e_pm.bind("<KeyRelease>", self.update_math)

        # --- DURATION PILL ---
        RoundedRect.draw(self.card, 26, 228, 374, 274, 14, "#1a1a1a", border_color="rgba(255,255,255,0.05)")
        self.card.create_text(42, 251, text="Duration", font=("Segoe UI", 13), fill="#888", anchor="w")
        
        self.var_dur = tk.StringVar(value=str(self.item.duration))
        ent_dur = tk.Entry(self.card, textvariable=self.var_dur, font=("Consolas", 14, "bold"), width=6,
                           bg="#1a1a1a", fg="#d4a843", relief="flat", justify="right", insertbackground=Colors.NEON_YELLOW)
        ent_dur.place(x=270, y=240, width=60)
        self.card.create_text(338, 251, text="min", font=("Consolas", 14, "bold"), fill="#d4a843", anchor="w")

        # --- FOOTER ---
        # Delete
        btn_del = tk.Label(self.card, text="Delete Block", font=("Segoe UI", 13), bg="#141414", fg="#FF453A", cursor="hand2")
        btn_del.place(x=26, y=380)
        btn_del.bind("<Button-1>", lambda e: self.delete())

        # Cancel
        self.btn_cancel = tk.Label(self.card, text="Cancel", font=("Segoe UI", 13), bg="#1c1c1c", fg="#888", cursor="hand2")
        self.btn_cancel.place(x=210, y=372, width=80, height=40)
        self.btn_cancel.bind("<Button-1>", lambda e: self.close())
        
        # Done
        self.btn_done = tk.Label(self.card, text="Done", font=("Segoe UI", 13, "bold"), bg="#d4a843", fg="#000", cursor="hand2")
        self.btn_done.place(x=300, y=372, width=74, height=40)
        self.btn_done.bind("<Button-1>", lambda e: self.save())
        
    def update_math(self, e=None):
        try:
            val_s = self.var_start.get().replace(".",":").split(":")
            val_e = self.var_end.get().replace(".",":").split(":")
            
            if len(val_s) == 2 and len(val_e) == 2:
                sh, sm = int(val_s[0]), int(val_s[1])
                eh, em = int(val_e[0]), int(val_e[1])
                
                # 12hr normalize
                if self.var_start_pm.get().upper() == "PM" and sh < 12: sh += 12
                if self.var_start_pm.get().upper() == "AM" and sh == 12: sh = 0
                if self.var_end_pm.get().upper() == "PM" and eh < 12: eh += 12
                if self.var_end_pm.get().upper() == "AM" and eh == 12: eh = 0
                
                diff = (eh * 60 + em) - (sh * 60 + sm)
                if diff < 0: diff += 24 * 60
                
                if diff > 0 and diff < 1440:
                    self.var_dur.set(str(diff))
        except: pass
        
    def save(self):
        # Reconstruct title with potentially updated times
        s = f"{self.var_start.get()} {self.var_start_pm.get()}".strip()
        e = f"{self.var_end.get()} {self.var_end_pm.get()}".strip()
        
        f_title = self.var_title.get()
        if s != "00:00" or e != "00:00":
             f_title = f"{s}-{e} • {f_title}"
             
        d = self.var_dur.get()
        self.on_save(self.item.id, f_title, d, self.lbl_icon.cget("text"))
        self.close()

    def delete(self):
        if messagebox.askyesno("Delete", "Delete this block?"):
            self.on_delete(self.item.id)
            self.close()

    def close(self):
        self.unbind_all("<Escape>")
        self.destroy()
        self.on_cancel()
