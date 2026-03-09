import logging
import threading
import httpx
from modules.supabase_credentials import get_supabase_headers, SUPABASE_URL
import database

logger = logging.getLogger(__name__)

# Known Supabase table schemas — only send columns that exist remotely
# If a column doesn't exist in Supabase, it gets stripped automatically
SUPABASE_COLUMNS = {
    "routines": ["id", "name", "description", "is_default", "created_at"],
    "routine_items": ["id", "routine_id", "title", "duration_minutes", "icon", "sort_order", "is_enabled"],
    "daily_logs": ["id", "date", "started_at", "completed_at", "total_time_seconds", "completion_rate", "notes"],
}

def _filter_rows(table: str, rows: list) -> list:
    """Filter row dicts to only include columns that exist in Supabase."""
    allowed = SUPABASE_COLUMNS.get(table)
    if not allowed:
        return rows
    return [{k: v for k, v in row.items() if k in allowed} for row in rows]

def _upsert_rows(table: str, rows: list, on_conflict: str = "id"):
    """Upsert rows into Supabase table using PostgREST."""
    if not rows:
        return
    headers = get_supabase_headers()
    
    # Filter to only Supabase-known columns
    rows = _filter_rows(table, rows)
    
    url = f"{SUPABASE_URL}/rest/v1/{table}?on_conflict={on_conflict}"
    
    # Send in batches of 50
    batch_size = 50
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i+batch_size]
        try:
            resp = httpx.post(url, headers=headers, json=batch, timeout=15.0)
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(f"Supabase upsert error for {table}: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Supabase connection error for {table}: {e}")
            raise
    
    logger.info(f"Synced {len(rows)} rows to {table}")

def sync_to_cloud():
    """Pushes local SQLite data to Supabase using REST APIs."""
    _upsert_rows("routines", database.get_all_routines(), on_conflict="id")
    _upsert_rows("routine_items", database.get_all_routine_items(), on_conflict="id")
    _upsert_rows("daily_logs", database.get_all_daily_logs(), on_conflict="date")
    return True

def sync_from_cloud():
    """Pulls data from Supabase and updates local SQLite."""
    get_headers = {k: v for k, v in get_supabase_headers().items() if k != "Prefer"}
    
    routines_resp = httpx.get(f"{SUPABASE_URL}/rest/v1/routines?select=*", headers=get_headers, timeout=15.0)
    routines_resp.raise_for_status()
    if routines_resp.json():
        database.upsert_routines(routines_resp.json())
        logger.info(f"Pulled {len(routines_resp.json())} routines from cloud.")

    items_resp = httpx.get(f"{SUPABASE_URL}/rest/v1/routine_items?select=*", headers=get_headers, timeout=15.0)
    items_resp.raise_for_status()
    if items_resp.json():
        database.upsert_routine_items(items_resp.json())
        logger.info(f"Pulled {len(items_resp.json())} routine items from cloud.")

    logs_resp = httpx.get(f"{SUPABASE_URL}/rest/v1/daily_logs?select=*", headers=get_headers, timeout=15.0)
    logs_resp.raise_for_status()
    if logs_resp.json():
        database.upsert_daily_logs(logs_resp.json())
        logger.info(f"Pulled {len(logs_resp.json())} daily logs from cloud.")
        
    return True

def auto_sync_push():
    """Fire-and-forget background sync after local edits."""
    def _run():
        try:
            sync_to_cloud()
        except Exception as e:
            logger.warning(f"Auto-sync failed (non-blocking): {e}")
    threading.Thread(target=_run, daemon=True).start()
