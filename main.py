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
