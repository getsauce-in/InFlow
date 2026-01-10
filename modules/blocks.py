from dataclasses import dataclass, asdict
from typing import List
import database
from modules import icons

@dataclass
class BlockItem:
    id: int
    title: str
    duration: int
    icon: str
    streak: int = 0
    total_minutes: int = 0
    is_completed: bool = False

class BlocksManager:
    def __init__(self):
        self.items = []
        self.routine_name = "Morning Session"
        self.refresh_items()

    def refresh_items(self):
        # We still query 'routine_items' table as per plan (schema unchanged)
        self.routine_name = database.get_active_routine_name()
        data = database.get_active_routine_items()
        self.items = [BlockItem(
            id=d['id'],
            title=d['title'],
            duration=d['duration_minutes'],
            icon=d['icon'],
            streak=d.get('current_streak', 0),
            total_minutes=d.get('total_minutes', 0)
        ) for d in data]

    def get_items(self) -> List[BlockItem]:
        return self.items

    def toggle_completion(self, item_id: int):
        # In a real app we might persist this daily state
        # For now, just in-memory session toggle for demo
        for item in self.items:
            if item.id == item_id:
                item.is_completed = not item.is_completed
                break
    
    def all_completed(self):
        return all(i.is_completed for i in self.items)

    def add_item(self, title, duration, icon):
        rid = database.get_default_routine_id()
        if rid:
            database.add_routine_item(rid, title, duration, icon)
            self.refresh_items()

    def update_item_optimistic(self, item_id, title, duration, icon):
        """Update local state immediately for instant UI feedback."""
        for item in self.items:
            if item.id == item_id:
                item.title = title
                item.duration = duration
                item.icon = icon
                break

    def update_item(self, item_id, title, duration, icon):
        """Persist change to DB and refresh."""
        database.update_routine_item(item_id, title, duration, icon)
        self.refresh_items()

    def delete_item(self, item_id):
        database.delete_routine_item(item_id)
        self.refresh_items()

    def reorder_items(self, item_ids: List[int]):
        database.update_routine_order(item_ids)
        self.refresh_items()

    def set_routine_name(self, name):
        database.update_active_routine_name(name)
        self.refresh_items()

    def get_next_icon(self, current):
        return icons.get_next_icon(current)

    def load_template(self, template_name):
        from modules import templates
        items = templates.get_template(template_name)
        if not items: return
        
        # 1. Clear existing
        current_ids = [i.id for i in self.items]
        conn = database.get_connection()
        c = conn.cursor()
        for iid in current_ids:
            c.execute("DELETE FROM routine_items WHERE id=?", (iid,))
        
        # 2. Add New
        # Need routine ID
        rid = database.get_default_routine_id()
        for i, item in enumerate(items):
            c.execute("INSERT INTO routine_items (routine_id, title, duration_minutes, icon, sort_order) VALUES (?, ?, ?, ?, ?)",
                      (rid, item['title'], item['duration'], item['icon'], i))
        
        # 3. Rename Routine
        c.execute("UPDATE routines SET name = ? WHERE id = ?", (template_name + " Session", rid))
        
        conn.commit()
        conn.close()
        self.refresh_items()
