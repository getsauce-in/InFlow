import tkinter as tk
import time
import os
import threading
from theme import Colors, Fonts, Metrics, Easing
from ui_components import NeonButton
from modules.session_logger import log_block_completion

BELL_SOUND = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
                          if "__file__" in dir() else ".", 
                          "assets", "soundreality-bell-fx-410608.mp3")

# Resolve relative to CWD as fallback
if not os.path.isabs(BELL_SOUND) or not os.path.exists(BELL_SOUND):
    BELL_SOUND = os.path.join("assets", "soundreality-bell-fx-410608.mp3")

def _play_bell():
    """Play the bell sound using Windows Media Player COM (zero dependencies)."""
    def _run():
        try:
            abs_path = os.path.abspath(BELL_SOUND)
            if not os.path.exists(abs_path):
                return
            import subprocess
            # Use PowerShell to play the mp3 via .NET SoundPlayer or Media.MediaPlayer
            ps_cmd = (
                f'Add-Type -AssemblyName PresentationCore; '
                f'$p = New-Object System.Windows.Media.MediaPlayer; '
                f'$p.Open([uri]"{abs_path}"); '
                f'$p.Play(); '
                f'Start-Sleep -Seconds 4; '
                f'$p.Close()'
            )
            subprocess.Popen(
                ["powershell", "-WindowStyle", "Hidden", "-Command", ps_cmd],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                creationflags=0x08000000  # CREATE_NO_WINDOW
            )
        except Exception:
            try:
                import winsound
                winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS | winsound.SND_ASYNC)
            except:
                pass
    threading.Thread(target=_run, daemon=True).start()

class BaseView(tk.Frame):
    def __init__(self, master, app_context):
        super().__init__(master, bg=Colors.BACKGROUND)
        self.app = app_context
        self.pack(fill="both", expand=True)

class ActiveRoutineView(BaseView):
    def __init__(self, master, app_context, routine_items, 
                 resume_index=None, resume_time=None, resume_paused=False):
        super().__init__(master, app_context)
        self.items = routine_items
        self.current_index = 0
        self.is_paused = False
        self.time_left = 0
        
        self.setup_ui()
        
        # Resume from saved state if provided
        if resume_index is not None and resume_index < len(self.items):
            self.current_index = resume_index
            item = self.items[resume_index]
            self.lbl_progress.config(text=f"STEP {resume_index + 1} OF {len(self.items)}")
            self.lbl_icon.config(text=item.icon)
            self.lbl_step.config(text=item.title)
            instructions = getattr(item, 'description', '')
            if not instructions.strip():
                instructions = "Focus on the current task. Remove all distractions."
            self.lbl_desc.config(text=instructions)
            self.time_left = resume_time if resume_time is not None else item.duration * 60
            self.is_paused = resume_paused
            self.update_timer_display()
            self.schedule_tick()
        else:
            self.start_step(0)

    def setup_ui(self):
        # Center Container
        self.center_frame = tk.Frame(self, bg=Colors.BACKGROUND)
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # 1. Step Title & Icon
        self.lbl_progress = tk.Label(self.center_frame, text="", font=("Segoe UI", 12, "bold"), 
                                     bg=Colors.BACKGROUND, fg=Colors.NEON_PURPLE)
        self.lbl_progress.pack(pady=(0, 10))

        self.lbl_icon = tk.Label(self.center_frame, text="", font=("Segoe UI Emoji", 56), 
                                 bg=Colors.BACKGROUND, fg=Colors.NEON_YELLOW)
        self.lbl_icon.pack(pady=(0, 15))
        
        self.lbl_step = tk.Label(self.center_frame, text="", font=Fonts.H1, 
                                 bg=Colors.BACKGROUND, fg=Colors.TEXT_PRIMARY)
        self.lbl_step.pack(pady=(0, 10))
        
        # 2. Timer
        self.lbl_timer = tk.Label(self.center_frame, text="00:00", font=Fonts.CINEMA, 
                                  bg=Colors.BACKGROUND, fg=Colors.TEXT_PRIMARY)
        self.lbl_timer.pack(pady=(0, 20))
        
        # 2.5 Focus Instructions
        self.lbl_desc = tk.Label(self.center_frame, text="", font=Fonts.H3, 
                                 bg=Colors.BACKGROUND, fg=Colors.TEXT_SECONDARY,
                                 wraplength=700, justify="center")
        self.lbl_desc.pack(pady=(0, 40))
        
        # 3. Controls
        self.controls_frame = tk.Frame(self.center_frame, bg=Colors.BACKGROUND)
        self.controls_frame.pack()
        
        self.btn_restart = NeonButton(self.controls_frame, text="Restart", width=140, height=50, 
                                      accent_color=Colors.ACCENT, command=self.restart_step)
        self.btn_restart.pack(side="left", padx=10)
        
        self.btn_pause = NeonButton(self.controls_frame, text="Pause", width=140, height=50, 
                                    accent_color=Colors.NEON_PURPLE, command=self.toggle_pause)
        self.btn_pause.pack(side="left", padx=10)
        
        self.btn_next = NeonButton(self.controls_frame, text="Next >", width=140, height=50, 
                                   accent_color=Colors.NEON_BLUE, command=self.next_step)
        self.btn_next.pack(side="left", padx=10)

    def start_step(self, index):
        if index >= len(self.items):
            self.finish_routine()
            return
            
        self.current_index = index
        item = self.items[index]
        
        # Update UI
        self.lbl_progress.config(text=f"STEP {index + 1} OF {len(self.items)}")
        self.lbl_icon.config(text=item.icon)
        self.lbl_step.config(text=item.title)
        
        instructions = getattr(item, 'description', '')
        if not instructions.strip():
            instructions = "Focus on the current task. Remove all distractions."
        self.lbl_desc.config(text=instructions)
        
        # Set Timer
        self.time_left = item.duration * 60
        self.update_timer_display()
        
        # Start Countdown
        self.is_paused = False
        self.btn_pause.text = "Pause"
        self.schedule_tick()
        
        # Play bell sound at block start
        _play_bell()

    def schedule_tick(self):
        if hasattr(self, 'timer_id'):
            self.after_cancel(self.timer_id)
        self.timer_id = self.after(1000, self.tick)

    def tick(self):
        if not self.is_paused and self.time_left > 0:
            self.time_left -= 1
            self.update_timer_display()
            
            if self.time_left <= 0:
                self.next_step()
                return
                
        self.schedule_tick()

    def update_timer_display(self):
        mins = self.time_left // 60
        secs = self.time_left % 60
        self.lbl_timer.config(text=f"{mins:02}:{secs:02}")

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        # Note: In a real NeonButton we'd expose a method to update text
        # For now visual feedback is minimal

    def restart_step(self):
        self.start_step(self.current_index)

    def next_step(self):
        # Log the completed block
        item = self.items[self.current_index]
        elapsed = (item.duration * 60) - self.time_left
        completed_mins = max(1, elapsed // 60)  # At least 1 min credit
        log_block_completion(item.title, completed_mins, item.icon)
        self.start_step(self.current_index + 1)

    def finish_routine(self):
        if hasattr(self, 'timer_id'):
            self.after_cancel(self.timer_id)
        # Clear any saved session — routine is complete
        self.app.active_session = None
        # Show Completion Screen
        for widget in self.winfo_children():
            widget.destroy()
            
        center = tk.Frame(self, bg=Colors.BACKGROUND)
        center.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(center, text="Session Complete", font=Fonts.H1, bg=Colors.BACKGROUND, fg=Colors.TEXT_PRIMARY).pack(pady=20)
        tk.Label(center, text="\"The only way to do great work is to love what you do.\"", font=Fonts.H3, 
                 bg=Colors.BACKGROUND, fg=Colors.TEXT_SECONDARY, wraplength=400).pack(pady=(0, 40))
                 
        NeonButton(center, text="Close", width=180, height=50, 
                   accent_color=Colors.NEON_TEAL, command=lambda: self.app.show_view("Home")).pack()
