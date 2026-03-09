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
        self.lbl_time.pack(pady=(0, 5))
        
        # 3. Date
        self.lbl_date = tk.Label(center_frame, text="", font=("Segoe UI", 16), 
                            bg=Colors.BACKGROUND, fg=Colors.TEXT_SECONDARY)
        self.lbl_date.pack(pady=(0, 40))
        
        self.update_clock()
        
        # 4. The One Button (Focus)
        if self.app.active_session:
            # Show Resume button prominently
            btn_resume = NeonButton(center_frame, text="Resume Session", width=220, height=60,
                                   accent_color=Colors.NEON_PURPLE, command=self.app.enter_focus_mode)
            btn_resume.pack(pady=(0, 10))
            
            saved = self.app.active_session
            step_info = f"Step {saved['index'] + 1} • {saved['time_left'] // 60}:{saved['time_left'] % 60:02d} remaining"
            tk.Label(center_frame, text=step_info, font=("Segoe UI", 11),
                     bg=Colors.BACKGROUND, fg=Colors.TEXT_SECONDARY).pack(pady=(0, 15))
            
            btn_new = NeonButton(center_frame, text="Start New Session", width=180, height=44,
                                 accent_color=Colors.ACCENT, 
                                 command=lambda: self._start_fresh())
            btn_new.pack()
        else:
            btn_focus = NeonButton(center_frame, text="Start Session", width=220, height=60,
                                   accent_color=Colors.ACCENT, command=self.app.enter_focus_mode)
            btn_focus.pack()
    
    def _start_fresh(self):
        self.app.active_session = None
        self.app.enter_focus_mode()

    def update_clock(self):
        now = datetime.datetime.now()
        current_time = now.strftime("%I:%M %p")
        current_date = now.strftime("%A, %d %B")
        
        self.lbl_time.config(text=current_time)
        self.lbl_date.config(text=current_date)
        
        self.after(1000, self.update_clock)
