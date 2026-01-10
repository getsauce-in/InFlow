
import sys
import traceback

def log(msg):
    print(msg)

try:
    log("Importing database...")
    import database
    log("Initializing database...")
    database.init_db()
    log("Database OK.")
    
    log("Importing app...")
    import app
    log("App imported module OK.")

    log("Testing BlocksManager...")
    from modules.blocks import BlocksManager
    bm = BlocksManager()
    items = bm.get_items()
    log(f"BlocksManager OK. Items: {len(items)}")
    
    log("Importing UI Components...")
    import ui_components
    log("UI Components OK.")
    
    log("All systems check passed.")

except Exception:
    traceback.print_exc()
