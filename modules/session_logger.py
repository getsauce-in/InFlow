"""
Session Logger — Append-only JSON array for tracking completed blocks.
Each entry records when a session block was completed during Focus Mode.
"""
import json
import os
import datetime
import logging

logger = logging.getLogger(__name__)

SESSIONS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sessions.json")

def _ensure_file():
    """Create data dir and sessions file if they don't exist."""
    os.makedirs(os.path.dirname(SESSIONS_FILE), exist_ok=True)
    if not os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

def log_block_completion(block_name: str, duration_minutes: int, icon: str = ""):
    """Log a completed block to sessions.json."""
    _ensure_file()
    now = datetime.datetime.now()
    
    entry = {
        "date": now.strftime("%Y-%m-%d"),
        "blockName": block_name,
        "startTime": (now - datetime.timedelta(minutes=duration_minutes)).strftime("%H:%M"),
        "endTime": now.strftime("%H:%M"),
        "durationMinutes": duration_minutes,
        "completed": True,
        "xpEarned": duration_minutes,  # 1 XP per minute
        "icon": icon,
    }
    
    try:
        with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        data = []
    
    data.append(entry)
    
    with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Logged completion: {block_name} ({duration_minutes}m, +{duration_minutes} XP)")
    return entry

def get_all_sessions() -> list:
    """Read all session records."""
    _ensure_file()
    try:
        with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def compute_analytics() -> dict:
    """Compute all analytics from session data."""
    sessions = get_all_sessions()
    today = datetime.date.today()
    
    # Group by date
    by_date = {}
    for s in sessions:
        d = s.get("date", "")
        if d not in by_date:
            by_date[d] = []
        by_date[d].append(s)
    
    # --- STREAK ---
    streak = 0
    check_date = today
    while True:
        ds = check_date.strftime("%Y-%m-%d")
        if ds in by_date and any(s.get("completed") for s in by_date[ds]):
            streak += 1
            check_date -= datetime.timedelta(days=1)
        else:
            break
    
    # --- FOCUS TIME (this week, Mon-Sun) ---
    week_start = today - datetime.timedelta(days=today.weekday())  # Monday
    focus_minutes_week = 0
    for i in range(7):
        d = (week_start + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        if d in by_date:
            focus_minutes_week += sum(s.get("durationMinutes", 0) for s in by_date[d])
    focus_hours_week = round(focus_minutes_week / 60, 1)
    
    # --- TOTAL XP ---
    total_xp = sum(s.get("xpEarned", 0) for s in sessions)
    
    # --- DAILY FOCUS (last 7 days) ---
    daily_focus = []
    for i in range(6, -1, -1):
        d = (today - datetime.timedelta(days=i))
        ds = d.strftime("%Y-%m-%d")
        day_name = d.strftime("%a")
        minutes = sum(s.get("durationMinutes", 0) for s in by_date.get(ds, []))
        daily_focus.append({
            "date": ds,
            "day": day_name,
            "minutes": minutes,
            "is_today": i == 0,
        })
    
    # --- BEST DAY ---
    best_day_name = "—"
    best_day_hours = 0
    for d, entries in by_date.items():
        total = sum(s.get("durationMinutes", 0) for s in entries)
        if total > best_day_hours * 60:
            best_day_hours = round(total / 60, 1)
            try:
                best_day_name = datetime.datetime.strptime(d, "%Y-%m-%d").strftime("%A")
            except:
                best_day_name = d
    
    # --- STREAK DOTS (this week Mon-Sun) ---
    streak_dots = []
    for i in range(7):
        d = (week_start + datetime.timedelta(days=i))
        ds = d.strftime("%Y-%m-%d")
        is_today = d == today
        filled = ds in by_date and any(s.get("completed") for s in by_date[ds])
        streak_dots.append({"filled": filled, "is_today": is_today})
    
    return {
        "streak": streak,
        "focus_hours_week": focus_hours_week,
        "focus_minutes_week": focus_minutes_week,
        "total_xp": total_xp,
        "daily_focus": daily_focus,
        "best_day_name": best_day_name,
        "best_day_hours": best_day_hours,
        "streak_dots": streak_dots,
        "total_sessions": len(sessions),
    }
