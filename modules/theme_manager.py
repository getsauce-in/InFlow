import json
import os

CONFIG_FILE = "theme_config.json"

THEMES = {
    "Carbon": {
        "BACKGROUND": "#0B0B0D",
        "NAV_BG": "#0B0B0D",
        "SURFACE_1": "#151517",
        "SURFACE_2": "#1C1C1E",
        "SURFACE_3": "#3A3A3C",
        "ACCENT": "#F5D142", # Gold
        "TEXT_PRIMARY": "#FFFFFF",
        "TEXT_SECONDARY": "#98989D"
    },
    "Midnight": {
        "BACKGROUND": "#050A14",
        "NAV_BG": "#050A14",
        "SURFACE_1": "#0A1428",
        "SURFACE_2": "#0F1E3C",
        "SURFACE_3": "#1E3C78",
        "ACCENT": "#00F0FF", # Cyan
        "TEXT_PRIMARY": "#E0F0FF",
        "TEXT_SECONDARY": "#8DA9C4"
    },
    "Forest": {
        "BACKGROUND": "#051405",
        "NAV_BG": "#051405",
        "SURFACE_1": "#0A280A",
        "SURFACE_2": "#0F3C0F",
        "SURFACE_3": "#1E501E",
        "ACCENT": "#50FF50", # Neon Green
        "TEXT_PRIMARY": "#E0FFE0",
        "TEXT_SECONDARY": "#8DC48D"
    },
     "Royal": {
        "BACKGROUND": "#140514",
        "NAV_BG": "#140514",
        "SURFACE_1": "#280A28",
        "SURFACE_2": "#3C0F3C",
        "SURFACE_3": "#501E50",
        "ACCENT": "#FF50FF", # Neon Pink
        "TEXT_PRIMARY": "#FFE0FF",
        "TEXT_SECONDARY": "#C48DC4"
    },
    "Sunset": {
        "BACKGROUND": "#140505",
        "NAV_BG": "#140505",
        "SURFACE_1": "#280A0A",
        "SURFACE_2": "#3C0F0F",
        "SURFACE_3": "#501E1E",
        "ACCENT": "#FF5050", # Red/Orange
        "TEXT_PRIMARY": "#FFE0E0",
        "TEXT_SECONDARY": "#C48D8D"
    }
}

class ThemeManager:
    @staticmethod
    def save_theme(theme_name):
        if theme_name not in THEMES: return
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump({"theme": theme_name}, f)
        except: pass

    @staticmethod
    def load_theme():
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    name = data.get("theme", "Carbon")
                    if name in THEMES:
                        return name, THEMES[name]
        except: pass
        return "Carbon", THEMES["Carbon"]

    @staticmethod
    def get_all_themes():
        return THEMES
