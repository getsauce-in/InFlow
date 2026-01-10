import tkinter as tk
from tkinter import messagebox
from theme import Colors, Metrics, Fonts
from ui_components import RoundedRect

class BlocksList(tk.Canvas):
    def __init__(self, master, app_context, width=600):
        super().__init__(master, width=width, bg=Colors.BACKGROUND, highlightthickness=0)
        self.app = app_context
        self.blocks_manager = self.app.blocks_manager
        self.items = []
        
        # Dimensions
        self.row_h = 54
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
        self.total_h = max(len(self.items) * self.row_h, 50) # Min height
        self.configure(height=self.total_h)
        
        # Group Background
        if self.items:
            RoundedRect.draw(self, 0, 0, self.content_w, self.total_h, Metrics.CORNER_RADIUS, Colors.SURFACE_1)

            for i, item in enumerate(self.items):
                y = i * self.row_h
                
                # Separator
                if i < len(self.items) - 1:
                     self.create_line(60, y + self.row_h, self.content_w - 20, y + self.row_h, 
                                      fill=Colors.SURFACE_3, width=1)
                
                tag = f"item_{i}"
                
                # Drag Handle
                self.create_text(30, y + self.row_h/2, text="≡", font=("Segoe UI", 16), fill=Colors.TEXT_TERTIARY, tags=tag)
                
                # Icon
                self.create_text(60, y + self.row_h/2, text=item.icon, font=("Segoe UI Emoji", 14), fill=Colors.ACCENT, tags=tag)
                
                # Title
                self.create_text(90, y + self.row_h/2, text=item.title, font=("Segoe UI", 12), fill=Colors.TEXT_PRIMARY, anchor="w", tags=tag)
                
                # Duration
                self.create_text(self.content_w - 50, y + self.row_h/2, text=f"{item.duration} min", font=("Segoe UI", 12), fill=Colors.TEXT_TERTIARY, anchor="e", tags=tag)
                
                # Delete
                del_tag = f"del_{i}"
                self.create_text(self.content_w - 20, y + self.row_h/2, text="✕", font=("Segoe UI", 14), fill=Colors.TEXT_TERTIARY, tags=(del_tag, "btn_del"))
                
                # Hitbox
                self.create_rectangle(0, y, self.content_w, y + self.row_h, fill="", outline="", tags=tag)
                
                self.tag_bind(tag, "<Button-1>", lambda e, idx=i: self.on_start_drag(e, idx))

    def on_hover(self, event):
        x, y = event.x, event.y
        idx = int(y // self.row_h)
        
        self.configure(cursor="")
        self.itemconfig("btn_del", fill=Colors.TEXT_TERTIARY)
        
        if 0 <= idx < len(self.items):
             # Delete Hover
             if x >= self.content_w - 40:
                 self.configure(cursor="hand2")
                 self.itemconfig(f"del_{idx}", fill="#E81123")
             # Drag Zone
             elif x <= 50:
                 self.configure(cursor="fleur")
             else:
                 self.configure(cursor="hand2")
                 
    def on_click(self, event):
         x, y = event.x, event.y
         idx = int(y // self.row_h)
         if 0 <= idx < len(self.items):
             if x >= self.content_w - 40:
                 self.delete_block(idx)
             elif x > 50:
                  # Edit
                  if hasattr(self, 'edit_callback'):
                      self.edit_callback(self.items[idx])
                  pass

    # --- DRAG LOGIC ---
    def on_start_drag(self, event, index):
        if event.x > 50: # Only drag via handle or left side
             if event.x < self.content_w - 40:
                 if hasattr(self, 'edit_callback'):
                    self.edit_callback(self.items[index])
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
