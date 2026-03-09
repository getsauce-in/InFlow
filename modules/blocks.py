from dataclasses import dataclass, asdict
from typing import List
import database
from modules import icons
from modules.sync_manager import auto_sync_push

@dataclass
class BlockItem:
    id: int
    title: str
    duration: int
    icon: str
    description: str = ""
    streak: int = 0
    total_minutes: int = 0
    is_completed: bool = False
    last_completed_date: str = None

class BlocksManager:
    def __init__(self):
        self.items = []
        self.routine_name = "Morning Session"
        self.refresh_items()
        
        # Auto-load curriculum
        self.auto_sync_curriculum()

    def refresh_items(self):
        # We still query 'routine_items' table as per plan (schema unchanged)
        self.routine_name = database.get_active_routine_name()
        data = database.get_active_routine_items()
        self.items = [BlockItem(
            id=d['id'],
            title=d['title'],
            duration=d['duration_minutes'],
            icon=d['icon'],
            description=d.get('description', ''),
            streak=d.get('current_streak', 0),
            total_minutes=d.get('total_minutes', 0),
            last_completed_date=d.get('last_completed_date')
        ) for d in data]

    def get_items(self) -> List[BlockItem]:
        return self.items

    def toggle_completion(self, item_id: int):
        import datetime
        today_str = datetime.date.today().isoformat()
        
        for item in self.items:
            if item.id == item_id:
                # Toggle internal state
                item.is_completed = not item.is_completed
                
                if item.is_completed:
                    # Logic when marking as DONE
                    # Check if already done today to avoid double counting
                    if item.last_completed_date == today_str:
                        # Already counted for today, just visual toggle?
                        # Or maybe we shouldn't have let it toggle if it was persisted as done?
                        # For now, let's assume we proceed but don't double increment streak
                        pass
                    else:
                        # Calculate Streak
                        new_streak = item.streak
                        yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
                        
                        if item.last_completed_date == yesterday:
                            new_streak += 1
                        else:
                            new_streak = 1 # Reset or start (unless it was today, handled above)
                            
                        item.streak = new_streak
                        item.total_minutes += item.duration
                        item.last_completed_date = today_str
                        
                        # Persist Stats
                        self.update_stats(item.id, item.streak, item.total_minutes, item.last_completed_date)
                        
                        # Award Focus XP
                        database.add_xp(item.duration * 10)
                        
                else:
                    # Logic when marking as UNDONE (Oops, didn't do it)
                    # If it was marked done today, we should revert stats
                    if item.last_completed_date == today_str:
                        item.streak = max(0, item.streak - 1)
                        item.total_minutes = max(0, item.total_minutes - item.duration)
                        # We don't know the exact previous date, but we can clear today.
                        # Setting to None or staying as today? 
                        # If we set to None, streak logic next time will reset to 1.
                        # If we leave it as today, next toggle will think it's done.
                        # Best effort: Set to yesterday so they can re-check it? 
                        # Or just leave it and let them re-check.
                        # Actually, if we decrement streak, we are assuming it was incremented today.
                        # Let's just rollback the values.
                        # To properly support undo, we'd need transaction history, but simple revert is fine.
                        pass  
                        
                        # Note: Simple undo is complex without history. 
                        # V1 Decision: Only persist POSITIVE completions for reliability. 
                        # Unchecking is visual only for the session.
                        pass

                break
    
    def update_stats(self, item_id, streak, total, date_str):
        conn = database.get_connection()
        c = conn.cursor()
        c.execute("UPDATE routine_items SET current_streak=?, total_minutes=?, last_completed_date=? WHERE id=?",
                  (streak, total, date_str, item_id))
        conn.commit()
        conn.close()

    def all_completed(self):
        return all(i.is_completed for i in self.items)

    def add_item(self, title, duration, icon):
        rid = database.get_default_routine_id()
        if rid:
            database.add_routine_item(rid, title, duration, icon)
            self.refresh_items()
            auto_sync_push()

    def update_item_optimistic(self, item_id, title, duration, icon, description=""):
        """Update local state immediately for instant UI feedback."""
        for item in self.items:
            if item.id == item_id:
                item.title = title
                item.duration = duration
                item.icon = icon
                item.description = description
                break

    def update_item(self, item_id, title, duration, icon, description=""):
        """Persist change to DB and refresh."""
        database.update_routine_item(item_id, title, duration, icon, description)
        self.refresh_items()
        auto_sync_push()

    def delete_item(self, item_id):
        database.delete_routine_item(item_id)
        self.refresh_items()
        auto_sync_push()

    def reorder_items(self, item_ids: List[int]):
        database.update_routine_order(item_ids)
        self.refresh_items()
        auto_sync_push()

    def set_routine_name(self, name):
        database.update_active_routine_name(name)
        self.refresh_items()
        auto_sync_push()

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
        auto_sync_push()

    def load_curriculum_day(self, day_name):
        import json
        import os
        
        filepath = os.path.join("assets", "curriculum.json")
        if not os.path.exists(filepath): return
            
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        if day_name not in data: return
        items = data[day_name]
        
        # 1. Clear existing
        current_ids = [i.id for i in self.items]
        conn = database.get_connection()
        c = conn.cursor()
        for iid in current_ids:
            c.execute("DELETE FROM routine_items WHERE id=?", (iid,))
            
        # 2. Add New
        rid = database.get_default_routine_id()
        for i, item in enumerate(items):
            # Fallback for duration safely 
            dur = item.get('duration_minutes', 60)
            
            # Format title with original time
            title = item['title']
            if 'original_time' in item:
                title = f"{item['original_time']} • {title}"
                
            # Assign specific motivation icons
            icon = "📘"
            lower_title = item['title'].lower()
            if "wake" in lower_title: icon = "🌅"
            elif "morning" in lower_title: icon = "☕"
            elif "python" in lower_title and "theory" in lower_title: icon = "📖"
            elif "python" in lower_title and "code" in lower_title: icon = "💻"
            elif "break" in lower_title or "rest" in lower_title or "free" in lower_title: icon = "🌴"
            elif "write" in lower_title: icon = "✍️"
            elif "dist" in lower_title or "reddit" in lower_title or "x" in lower_title: icon = "📱"
            elif "review" in lower_title: icon = "📝"
            elif "wind down" in lower_title: icon = "🌙"
            elif "sleep" in lower_title: icon = "💤"
            elif "linux" in lower_title: icon = "🐧"
            elif "git" in lower_title: icon = "🐙"
            elif "plan" in lower_title: icon = "🗓️"

            c.execute("INSERT INTO routine_items (routine_id, title, duration_minutes, icon, description, sort_order) VALUES (?, ?, ?, ?, ?, ?)",
                      (rid, title, dur, icon, item.get('description', ''), i))
                      
        # 3. Rename Routine
        c.execute("UPDATE routines SET name = ? WHERE id = ?", (f"Curriculum: {day_name}", rid))
        
        conn.commit()
        conn.close()
        self.refresh_items()
        auto_sync_push()

    def auto_sync_curriculum(self):
        import datetime
        start_date_str = database.get_curriculum_start_date()
        if not start_date_str: return
        
        start = datetime.date.fromisoformat(start_date_str)
        today = datetime.date.today()
        days_diff = (today - start).days
        if days_diff < 0: days_diff = 0
        
        day_num = days_diff + 1
        day_key = f"Day {day_num}"
        
        # Auto-load if the current routine name does not match the computed day and the day exists
        if self.routine_name != f"Curriculum: {day_key}":
            # Just do a lazy check to see if we have this day in JSON before trying
            import os, json
            if os.path.exists(os.path.join("assets", "curriculum.json")):
                with open(os.path.join("assets", "curriculum.json"), "r", encoding="utf-8") as f:
                    curr_data = json.load(f)
                if day_key in curr_data:
                    self.load_curriculum_day(day_key)
