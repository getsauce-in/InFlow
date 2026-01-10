import tkinter as tk
from theme import Colors

class BaseView(tk.Frame):
    def __init__(self, master, app_context):
        super().__init__(master, bg=Colors.BACKGROUND)
        self.app = app_context
        self.pack(fill="both", expand=True)
