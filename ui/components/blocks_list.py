import tkinter as tk
from tkinter import messagebox
from theme import Colors, Metrics, Fonts
from ui_components import RoundedRect

class BlocksList(tk.Canvas):
    def __init__(self, master, app_context, width=800):
        super().__init__(master, width=width, bg=Colors.BACKGROUND, highlightthickness=0)
        self.app = app_context
        self.blocks_manager = self.app.blocks_manager
        self.items = []
        self.expanded_idx = None
        self.edit_vars = {} # Holds StringVars for the inline editor
        
        # Dimensions
        self.row_h = 110
        self.content_w = width
        self.total_h = 0
        
        # Drag Data
        self.drag_data = {"item_index": None, "y_start": 0, "dragging": False}
        
        self.bind("<Button-1>", self.on_click)
        self.bind("<Motion>", self.on_hover)
        
        self.refresh()

    def refresh(self):
        self.items = self.blocks_manager.get_items()
        self.render()
        
    def render(self):
        self.delete("all")
        
        # Destroy old edit entries if any
        for w in self.winfo_children():
            w.destroy()
            
        # Calculate total height dynamically based on expanded state
        self.total_h = 0
        for i in range(len(self.items)):
             if i == self.expanded_idx:
                 self.total_h += 340 # Expanded height
             else:
                 self.total_h += self.row_h
                 
        self.total_h = max(self.total_h, 50) # Min height
        self.configure(height=self.total_h)
        
        # Group Background
        if self.items:
            # RoundedRect base
            RoundedRect.draw(self, 0, 0, self.content_w, self.total_h, Metrics.CORNER_RADIUS, Colors.SURFACE_1)

            current_y = 0
            for i, item in enumerate(self.items):
                is_expanded = (i == self.expanded_idx)
                my_h = 340 if is_expanded else self.row_h
                y = current_y
                tag = f"item_{i}"
                
                # Base hover rect
                self.create_rectangle(0, y, self.content_w, y + my_h, fill="", outline="", tags=(tag, f"bg_{i}"))
                
                # Left accent
                self.create_rectangle(0, y, 2, y + my_h, fill=Colors.NEON_YELLOW, outline="", tags=(tag, f"accent_{i}"), state="hidden")
                
                if is_expanded:
                    # Draw expanded active background
                    self.create_rectangle(0, y, self.content_w, y + my_h, fill="#1c1c1c", outline="", tags=tag)
                    self.create_rectangle(0, y, 2, y + my_h, fill=Colors.NEON_YELLOW, outline="", tags=tag)
                
                # Separator
                if i < len(self.items) - 1:
                     self.create_line(0, y + my_h, self.content_w, y + my_h, fill=Colors.SURFACE_3, width=1)
                
                # Drag Handle
                self.create_text(20, y + self.row_h/2, text="⠿", font=("Consolas", 14), fill=Colors.TEXT_TERTIARY, tags=tag)
                
                # --- PARSE TIME & DATA ---
                parts = item.title.split(" • ", 1)
                t_str = parts[0] if len(parts) > 1 else ""
                real_t = parts[1] if len(parts) > 1 else item.title
                
                t_start, t_end = t_str, ""
                if "–" in t_str: t_start, t_end = t_str.split("–", 1)
                elif "-" in t_str: t_start, t_end = t_str.split("-", 1)
                
                # --- RENDER COLS (Standard Top Row) ---
                
                # 1. Time Col
                self.create_text(40, y + self.row_h/2 - 8, text=t_start.strip(), font=("Consolas", 11, "bold"), fill=Colors.NEON_YELLOW, anchor="w", tags=tag)
                self.create_text(40, y + self.row_h/2 + 8, text=t_end.strip(), font=("Consolas", 9), fill=Colors.TEXT_TERTIARY, anchor="w", tags=tag)
                self.create_line(130, y, 130, y+self.row_h, fill=Colors.SURFACE_3)
                
                # 2. Icon Col
                self.create_text(155, y + self.row_h/2, text=item.icon, font=("Segoe UI Emoji", 18), fill=Colors.NEON_YELLOW, tags=tag)
                self.create_line(180, y, 180, y+self.row_h, fill=Colors.SURFACE_3)
                
                # 3. Label Col
                self.create_text(196, y + self.row_h/2 - 16, text=real_t, font=("Segoe UI", 13, "bold"), fill=Colors.TEXT_PRIMARY, anchor="w", tags=tag)
                
                sub = item.description if hasattr(item, 'description') else ""
                if sub:
                    self.create_text(196, y + self.row_h/2 + 14, text=sub, font=("Consolas", 9), fill="#EEF2FF", anchor="w", width=460, tags=tag)

                # 4. Duration Pill
                is_long = item.duration >= 45
                p_col = Colors.NEON_YELLOW if is_long else Colors.TEXT_TERTIARY
                
                pill_cx = self.content_w - 90
                self.create_rectangle(pill_cx - 34, y + self.row_h/2 - 12, pill_cx + 34, y + self.row_h/2 + 12, outline=p_col, fill="#1c1810" if is_long else "", tags=tag)
                self.create_text(pill_cx, y + self.row_h/2, text=f"{item.duration} min", font=("Consolas", 10, "bold"), fill=p_col, tags=tag)
                self.create_line(self.content_w - 46, y, self.content_w - 46, y+self.row_h, fill=Colors.SURFACE_3)
                
                # 5. Config/Toggle Col (Replaces Delete)
                cfg_tag = f"cfg_{i}"
                self.create_text(self.content_w - 23, y + self.row_h/2, text="▲" if is_expanded else "▼", font=("Segoe UI", 10), fill=Colors.TEXT_TERTIARY, tags=(cfg_tag, "btn_cfg"))
                
                # --- INLINE EXPANDED RENDER ---
                if is_expanded:
                    self._render_inline_editor(i, item, y + self.row_h)

                self.tag_bind(tag, "<Button-1>", lambda e, idx=i: self.on_start_drag(e, idx))
                
                current_y += my_h

    def _render_inline_editor(self, idx, item, y_start):
        import tkinter as tk
        from theme import Colors
        
        # Parse for editing
        parts = item.title.split(" • ", 1)
        t_str = parts[0] if len(parts) > 1 else ""
        real_t = parts[1] if len(parts) > 1 else item.title
        
        s_val, s_pm = "00:00", "AM"
        e_val, e_pm = "00:00", "AM"
        if t_str:
            t_start, *t_end = t_str.split("-") if "-" in t_str else t_str.split("–")
            if t_start:
                s = t_start.strip().split(" ")
                s_val = s[0]
                if len(s) > 1: s_pm = s[1]
            if t_end:
                e = t_end[0].strip().split(" ")
                e_val = e[0]
                if len(e) > 1: e_pm = e[1]
                
        # Vars
        v_title = tk.StringVar(value=real_t)
        v_s = tk.StringVar(value=s_val)
        v_spm = tk.StringVar(value=s_pm)
        v_e = tk.StringVar(value=e_val)
        v_epm = tk.StringVar(value=e_pm)
        v_dur = tk.StringVar(value=str(item.duration))
        
        self.edit_vars = {'title': v_title, 's': v_s, 'spm': v_spm, 'e': v_e, 'epm': v_epm, 'dur': v_dur, 'icon': item.icon}
        
        def update_math(*args):
            try:
                val_s = v_s.get().replace(".",":").split(":")
                val_e = v_e.get().replace(".",":").split(":")
                if len(val_s) == 2 and len(val_e) == 2:
                    sh, sm = int(val_s[0]), int(val_s[1])
                    eh, em = int(val_e[0]), int(val_e[1])
                    if v_spm.get().upper() == "PM" and sh < 12: sh += 12
                    if v_spm.get().upper() == "AM" and sh == 12: sh = 0
                    if v_epm.get().upper() == "PM" and eh < 12: eh += 12
                    if v_epm.get().upper() == "AM" and eh == 12: eh = 0
                    diff = (eh * 60 + em) - (sh * 60 + sm)
                    if diff < 0: diff += 24 * 60
                    if 0 < diff < 1440: v_dur.set(str(diff))
            except: pass
            
        v_s.trace_add("write", update_math); v_e.trace_add("write", update_math)
        v_spm.trace_add("write", update_math); v_epm.trace_add("write", update_math)

        # UI Drawing
        self.create_line(40, y_start, self.content_w - 40, y_start, fill=Colors.SURFACE_3, dash=(4,4))
        
        # Name
        self.create_text(40, y_start + 20, text="TASK NAME", fill="#666", font=("Segoe UI", 9, "bold"), anchor="w")
        e_title = tk.Entry(self, textvariable=v_title, font=("Segoe UI", 12, "bold"), bg="#1a1a1a", fg="#fff", insertbackground=Colors.NEON_YELLOW, relief="flat", highlightbackground="#333", highlightthickness=1)
        self.create_window(40, y_start + 50, window=e_title, anchor="w", width=300, height=36)
        e_title.bind("<Return>", lambda e: self.save_expanded())
        
        # Duration Direct
        self.create_text(370, y_start + 20, text="DUR (min)", fill="#666", font=("Segoe UI", 9, "bold"), anchor="w")
        e_dur = tk.Entry(self, textvariable=v_dur, font=("Segoe UI", 12, "bold"), bg="#1a1a1a", fg=Colors.NEON_YELLOW, insertbackground=Colors.NEON_YELLOW, relief="flat", highlightbackground="#333", highlightthickness=1, justify="center")
        self.create_window(370, y_start + 50, window=e_dur, anchor="w", width=60, height=36)
        e_dur.bind("<Return>", lambda e: self.save_expanded())
        
        # Time Overrides
        self.create_text(460, y_start + 20, text="START / END TIME", fill="#666", font=("Segoe UI", 9, "bold"), anchor="w")
        fs1 = tk.Entry(self, textvariable=v_s, font=("Consolas", 12,"bold"), bg="#1a1a1a", fg="#fff", insertbackground=Colors.NEON_YELLOW, relief="flat", highlightbackground="#333", highlightthickness=1, justify="center")
        self.create_window(460, y_start + 50, window=fs1, anchor="w", width=54, height=36)
        fs2 = tk.Entry(self, textvariable=v_spm, font=("Segoe UI", 10,"bold"), bg="#1a1a1a", fg="#888", insertbackground="#888", relief="flat", highlightbackground="#333", highlightthickness=1, justify="center")
        self.create_window(518, y_start + 50, window=fs2, anchor="w", width=36, height=36)
        
        fe1 = tk.Entry(self, textvariable=v_e, font=("Consolas", 12,"bold"), bg="#1a1a1a", fg="#fff", insertbackground=Colors.NEON_YELLOW, relief="flat", highlightbackground="#333", highlightthickness=1, justify="center")
        self.create_window(570, y_start + 50, window=fe1, anchor="w", width=54, height=36)
        fe2 = tk.Entry(self, textvariable=v_epm, font=("Segoe UI", 10,"bold"), bg="#1a1a1a", fg="#888", insertbackground="#888", relief="flat", highlightbackground="#333", highlightthickness=1, justify="center")
        self.create_window(628, y_start + 50, window=fe2, anchor="w", width=36, height=36)

        # Description
        self.create_text(40, y_start + 100, text="DESCRIPTION", fill="#666", font=("Segoe UI", 9, "bold"), anchor="w")
        e_desc = tk.Text(self, font=("Segoe UI", 10), bg="#1a1a1a", fg="#fff", insertbackground=Colors.NEON_YELLOW, relief="flat", highlightbackground="#333", highlightthickness=1)
        e_desc.insert("1.0", getattr(item, 'description', ''))
        self.create_window(40, y_start + 120, window=e_desc, anchor="nw", width=624, height=70)
        self.edit_vars['desc_widget'] = e_desc

        # Buttons
        bd = tk.Label(self, text="Delete Block", font=("Segoe UI", 10), bg="#1c1c1c", fg="#FF453A", cursor="hand2")
        self.create_window(40, y_start + 210, window=bd, anchor="w")
        bd.bind("<Button-1>", lambda e: self.delete_block(idx))
        
        bc = tk.Label(self, text="Cancel", font=("Segoe UI", 10), bg="#222", fg="#888", cursor="hand2")
        self.create_window(self.content_w - 140, y_start + 210, window=bc, anchor="w", width=60, height=30)
        bc.bind("<Button-1>", lambda e: self.toggle_expand(idx))
        
        bs = tk.Label(self, text="Save", font=("Segoe UI", 10, "bold"), bg=Colors.NEON_YELLOW, fg="#000", cursor="hand2")
        self.create_window(self.content_w - 60, y_start + 210, window=bs, anchor="w", width=60, height=30)
        bs.bind("<Button-1>", lambda e: self.save_expanded())

    def save_expanded(self):
        if self.expanded_idx is None: return
        import threading
        i = self.items[self.expanded_idx]
        v = self.edit_vars
        
        s = f"{v['s'].get()} {v['spm'].get()}".strip()
        e = f"{v['e'].get()} {v['epm'].get()}".strip()
        
        f_title = v['title'].get()
        if s != "00:00" or e != "00:00":
             f_title = f"{s}-{e} • {f_title}"
             
        try: d = int(v['dur'].get())
        except: d = i.duration
        if d < 1: d = 1
        
        f_desc = v['desc_widget'].get("1.0", "end-1c").strip() if 'desc_widget' in v else getattr(i, 'description', '')
        
        # Optimistic
        self.blocks_manager.update_item_optimistic(i.id, f_title, d, v.get('icon', i.icon), f_desc)
        self.expanded_idx = None
        self.refresh()
        
        def _bg():
            self.blocks_manager.update_item(i.id, f_title, d, v.get('icon', i.icon), f_desc)
        threading.Thread(target=_bg, daemon=True).start()

    def on_hover(self, event):
        x, y = event.x, event.y
        # Convert y to logical index accounting for expanded rows
        idx = -1
        cy = 0
        for i in range(len(self.items)):
            h = 340 if i == self.expanded_idx else self.row_h
            if cy <= y < cy + h:
                idx = i
                break
            cy += h
            
        self.configure(cursor="")
        self.itemconfig("btn_cfg", fill=Colors.TEXT_TERTIARY)
        # Reset hovers
        for i in range(len(self.items)):
             self.itemconfig(f"bg_{i}", fill="")
             if i != self.expanded_idx:
                 self.itemconfig(f"accent_{i}", state="hidden")
        
        if 0 <= idx < len(self.items):
             self.itemconfig(f"bg_{idx}", fill=Colors.SURFACE_2)
             self.itemconfig(f"accent_{idx}", state="normal")
             
             if x >= self.content_w - 46:
                 self.configure(cursor="hand2")
                 self.itemconfig(f"cfg_{idx}", fill=Colors.NEON_YELLOW)
             elif x <= 50:
                 self.configure(cursor="fleur")
             else:
                 self.configure(cursor="")
                 
    def on_click(self, event):
         x, y = event.x, event.y
         idx = -1
         cy = 0
         for i in range(len(self.items)):
             h = 340 if i == self.expanded_idx else self.row_h
             if cy <= y < cy + h:
                 idx = i
                 break
             cy += h
             
         if 0 <= idx < len(self.items):
             if x >= self.content_w - 46:
                 self.toggle_expand(idx)
             elif x > 50 and idx != self.expanded_idx:
                  self.toggle_expand(idx)

    def toggle_expand(self, idx):
         if self.expanded_idx == idx:
             self.expanded_idx = None
         else:
             self.expanded_idx = idx
         self.refresh()

    def on_start_drag(self, event, index):
        if event.x > 50: # Only drag via handle or left side
             if event.x < self.content_w - 46:
                 self.toggle_expand(index)
             return
             
        self.drag_data = {"item_index": index, "y_start": event.y, "dragging": False, "last_y": event.y}
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_release)
        
    def on_drag(self, event):
        if self.drag_data["item_index"] is not None:
             if not self.drag_data["dragging"] and abs(event.y - self.drag_data["y_start"]) > 5:
                 self.drag_data["dragging"] = True
                 self.tag_raise(f"item_{self.drag_data['item_index']}")
                 
             if self.drag_data["dragging"]:
                 dy = event.y - self.drag_data["last_y"]
                 self.move(f"item_{self.drag_data['item_index']}", 0, dy)
                 self.drag_data["last_y"] = event.y

    def on_release(self, event):
        self.unbind("<B1-Motion>")
        self.unbind("<ButtonRelease-1>")
        if self.drag_data["dragging"]:
            # Calc new pos
            y = event.y
            target = int(y // self.row_h)
            target = max(0, min(target, len(self.items)-1))
            
            src = self.drag_data["item_index"]
            if src != target:
                items = self.blocks_manager.items[:]
                item = items.pop(src)
                items.insert(target, item)
                self.blocks_manager.reorder_items([x.id for x in items])
            self.refresh()
        
        self.drag_data["item_index"] = None
        self.drag_data["dragging"] = False

    def delete_block(self, idx):
        if messagebox.askyesno("Delete", "Delete this block?"):
            self.blocks_manager.delete_item(self.items[idx].id)
            self.refresh()
            
    def set_callbacks(self, edit_cb):
        self.edit_callback = edit_cb
