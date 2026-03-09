import os
import sys
from dotenv import load_dotenv
load_dotenv()  # Load .env before anything else

# Windows: Set AppUserModelID BEFORE importing Tkinter
# This tells Windows to treat InFlow as its own app (not grouped under python.exe)
# which allows the custom icon to show in the taskbar
try:
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("inflow.app.1.0")
except Exception:
    pass

from app import Flow
import time

try:
    if __name__ == "__main__":
        import database
        database.init_db()
        app = Flow()
        app.mainloop()
except Exception as e:
    import traceback
    import ctypes
    
    error_msg = f"An unexpected error occurred:\n{str(e)}\n\nSee console/log for details."
    traceback.print_exc()
    
    # Try using ctypes to show a native message box (Works even if Tkinter fails)
    try:
        ctypes.windll.user32.MessageBoxW(0, error_msg, "InFlow Error", 0x10)
    except:
        print("Could not show error dialog.")
