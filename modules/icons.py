
# Categorized Icon Library for InFlow
# Sticking to standard emojis for maximum compatibility and "zen" feel without custom assets.

ICONS = {
    "Morning": ["☀️", "🌅", "🍳", "☕", "🧘", "🚿", "🦷", "🧴"],
    "Deep Work": ["🧠", "⚡", "💻", "📝", "📚", "🔬", "🎨", "🎹"],
    "Health": ["💪", "🏃", "🥗", "💊", "🥤", "🍎", "🚴", "🚶"],
    "Evening": ["🌙", "📖", "🍵", "🕯️", "🛌", "🛀", "📵", "🥱"],
    "Breaks": ["🛑", "🌴", "🎵", "🎮", "💬", "🚶‍♂️", "🥪", "👀"],
    "Chores": ["🧹", "🧺", "🧼", "🛒", "🔧", "🪴", "🗑️", "🧽"]
}

DEFAULT_ICON = "🟦"

def get_all_icons():
    """Returns a flat list of all unique icons."""
    all_icons = []
    seen = set()
    for category in ICONS.values():
        for icon in category:
            if icon not in seen:
                all_icons.append(icon)
                seen.add(icon)
    return all_icons

def get_next_icon(current_icon):
    """Cycles through icons for a simple picker if needed."""
    all_i = get_all_icons()
    if current_icon in all_i:
        idx = all_i.index(current_icon)
        return all_i[(idx + 1) % len(all_i)]
    return all_i[0]
