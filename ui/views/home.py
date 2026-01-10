import tkinter as tk
import datetime
from theme import Colors, Fonts
from ui_components import NeonButton
from ui.views.base import BaseView

class HomeView(BaseView):
    def __init__(self, master, app_context):
        super().__init__(master, app_context)
        self.setup()

    def setup(self):
        # CENETERED LAYOUT - ZEN MODE
        
        # Center Container
        center_frame = tk.Frame(self, bg=Colors.BACKGROUND)
        center_frame.place(relx=0.5, rely=0.45, anchor="center")
        
        # 1. Greeting (Subtle)
        hour = datetime.datetime.now().hour
        greeting = "Good Morning"
        if hour >= 12: greeting = "Good Afternoon"
        if hour >= 18: greeting = "Good Evening"
        
        lbl_greet = tk.Label(center_frame, text=greeting, font=Fonts.H2, 
                             bg=Colors.BACKGROUND, fg=Colors.TEXT_SECONDARY)
        lbl_greet.pack(pady=(0, 10))
        
        # 2. Massive Time (Cinematic)
        self.lbl_time = tk.Label(center_frame, text="", font=Fonts.CINEMA, 
                            bg=Colors.BACKGROUND, fg=Colors.TEXT_PRIMARY)
        self.lbl_time.pack(pady=(0, 40))
        self.update_clock()
        
        # 3. The One Button (Focus)
        btn_focus = NeonButton(center_frame, text="Start Session", width=220, height=60,
                               accent_color=Colors.ACCENT, command=self.app.enter_focus_mode)
        btn_focus.pack()

    def update_clock(self):
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        self.lbl_time.config(text=current_time)
        self.after(1000, self.update_clock)
