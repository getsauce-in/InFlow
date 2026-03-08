import logging
import httpx
from modules.supabase_credentials import get_supabase_headers, SUPABASE_URL
import database

logger = logging.getLogger(__name__)

def sync_to_cloud():
    """Pushes local SQLite data to Supabase using REST APIs."""
    headers = get_supabase_headers()
    
    # 1. Sync Routines
    routines = database.get_all_routines()
    if routines:
        resp = httpx.post(f"{SUPABASE_URL}/rest/v1/routines", headers=headers, json=routines)
        resp.raise_for_status()
        logger.info(f"Synced {len(routines)} routines to cloud.")

    # 2. Sync Routine Items
    items = database.get_all_routine_items()
    if items:
        resp = httpx.post(f"{SUPABASE_URL}/rest/v1/routine_items", headers=headers, json=items)
        resp.raise_for_status()
        logger.info(f"Synced {len(items)} routine items to cloud.")
        
    # 3. Sync Daily Logs
    logs = database.get_all_daily_logs()
    if logs:
        resp = httpx.post(f"{SUPABASE_URL}/rest/v1/daily_logs", headers=headers, json=logs)
        resp.raise_for_status()
        logger.info(f"Synced {len(logs)} daily logs to cloud.")

    return True

def sync_from_cloud():
    """Pulls data from Supabase and updates local SQLite."""
    # We remove the 'Prefer' header to just do a standard GET
    headers = get_supabase_headers()
    if "Prefer" in headers:
        del headers["Prefer"]
    
    # 1. Pull Routines
    routines_resp = httpx.get(f"{SUPABASE_URL}/rest/v1/routines?select=*", headers=headers)
    routines_resp.raise_for_status()
    routines_data = routines_resp.json()
    if routines_data:
        database.upsert_routines(routines_data)
        logger.info(f"Pulled {len(routines_data)} routines from cloud.")

    # 2. Pull Routine Items
    items_resp = httpx.get(f"{SUPABASE_URL}/rest/v1/routine_items?select=*", headers=headers)
    items_resp.raise_for_status()
    items_data = items_resp.json()
    if items_data:
        database.upsert_routine_items(items_data)
        logger.info(f"Pulled {len(items_data)} routine items from cloud.")

    # 3. Pull Daily Logs
    logs_resp = httpx.get(f"{SUPABASE_URL}/rest/v1/daily_logs?select=*", headers=headers)
    logs_resp.raise_for_status()
    logs_data = logs_resp.json()
    if logs_data:
        database.upsert_daily_logs(logs_data)
        logger.info(f"Pulled {len(logs_data)} daily logs from cloud.")
        
    return True
