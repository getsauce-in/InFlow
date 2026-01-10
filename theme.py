"""
Flow Design System v2.0 - Project Lamborghini
Ultra-premium dark mode aesthetics.
"""

from modules.theme_manager import ThemeManager

# Load Theme Data on Import
CURRENT_THEME, T_DATA = ThemeManager.load_theme()

class Colors:
    # Loaded Attributes
    BACKGROUND = T_DATA["BACKGROUND"]
    NAV_BG = T_DATA["NAV_BG"]
    SURFACE_1 = T_DATA["SURFACE_1"]
    SURFACE_2 = T_DATA["SURFACE_2"]
    SURFACE_3 = T_DATA["SURFACE_3"]
    ACCENT = T_DATA["ACCENT"]
    
    # Aliases
    NEON_BLUE = ACCENT
    NEON_PURPLE = ACCENT
    NEON_YELLOW = ACCENT
    NEON_TEAL = ACCENT
    
    DANGER = "#FF453A"
    SUCCESS = "#30D158"

    # Text
    TEXT_PRIMARY = T_DATA["TEXT_PRIMARY"]
    TEXT_SECONDARY = T_DATA["TEXT_SECONDARY"]
    TEXT_TERTIARY = "#505055" 
    
    # Borders & Glows
    BORDER_LIGHT = SURFACE_3 # Dynamic
    GLOW_BLUE = ACCENT
    
    @classmethod
    def update(cls, t_data):
        cls.BACKGROUND = t_data["BACKGROUND"]
        cls.NAV_BG = t_data["NAV_BG"]
        cls.SURFACE_1 = t_data["SURFACE_1"]
        cls.SURFACE_2 = t_data["SURFACE_2"]
        cls.SURFACE_3 = t_data["SURFACE_3"]
        cls.ACCENT = t_data["ACCENT"]
        cls.NEON_BLUE = cls.ACCENT
        cls.NEON_PURPLE = cls.ACCENT
        cls.NEON_YELLOW = cls.ACCENT
        cls.NEON_TEAL = cls.ACCENT
        cls.TEXT_PRIMARY = t_data["TEXT_PRIMARY"]
        cls.TEXT_SECONDARY = t_data["TEXT_SECONDARY"]
        cls.BORDER_LIGHT = cls.SURFACE_3
        cls.GLOW_BLUE = cls.ACCENT
    
class Fonts:
    # Font Families
    PRIMARY = "Segoe UI"         # Reverted to Native Windows feel
    
    # Typography Scale
    CINEMA = (PRIMARY, 64, "bold") # Massive time display (Reduced from 72)
    DISPLAY = (PRIMARY, 36, "bold") # Reduced from 42
    H1 = (PRIMARY, 24, "bold")      # Reduced from 32
    H2 = (PRIMARY, 16, "bold")      # Reduced from 20
    H3 = (PRIMARY, 14, "bold")      # Reduced from 16
    
    BODY_L = (PRIMARY, 10)       # Smaller
    BODY = (PRIMARY, 9)          # Smaller for dense info (Navbar)
    CAPTION = (PRIMARY, 9)
    
    MONO = ("Consolas", 10)

class Metrics:
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 850
    SIDEBAR_WIDTH = 80       # Slimmer, icon-focused sidebar
    CORNER_RADIUS = 20       # Aggressive rounding
    PADDING_L = 30
    BUTTON_HEIGHT = 44
    
class Easing:
    # Animation constants
    DURATION_FAST = 200      # ms
    DURATION_NORMAL = 400    # ms
