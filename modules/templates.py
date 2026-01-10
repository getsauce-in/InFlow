
from modules.icons import ICONS

def get_template(name):
    # Helper: Access categories safely
    morn = ICONS["Morning"]
    deep = ICONS["Deep Work"]
    health = ICONS["Health"]
    eve = ICONS["Evening"]
    brk = ICONS["Breaks"]

    if name == "Morning":
        return [
            {"title": "Make Bed & Hydrate", "duration": 5, "icon": health[4]}, # 🥤
            {"title": "Meditation", "duration": 10, "icon": morn[4]}, # 🧘
            {"title": "Deep Work / Writing", "duration": 45, "icon": deep[3]}, # 📝
            {"title": "Shower & Ready", "duration": 20, "icon": morn[5]}, # 🚿
        ]
    elif name == "Deep Work":
        return [
            {"title": "Clear Distractions", "duration": 5, "icon": deep[1]}, # ⚡
            {"title": "Deep Focus Session", "duration": 60, "icon": deep[0]}, # 🧠
            {"title": "Active Break", "duration": 15, "icon": brk[1]}, # 🌴
            {"title": "Deep Focus Session", "duration": 60, "icon": deep[2]}, # 💻
        ]
    elif name == "Study":
        return [
            {"title": "Review Goals", "duration": 5, "icon": deep[4]}, # 📚
            {"title": "Core Study Block", "duration": 50, "icon": deep[5]}, # 🔬
            {"title": "Recall / Notes", "duration": 15, "icon": deep[3]}, # 📝
            {"title": "Stretch", "duration": 5, "icon": health[7]}, # 🚶
        ]
    elif name == "Evening":
        return [
            {"title": "Disconnect", "duration": 10, "icon": eve[6]}, # 📵
            {"title": "Plan Tomorrow", "duration": 10, "icon": deep[3]}, # 📝
            {"title": "Reading", "duration": 30, "icon": eve[1]}, # 📖
            {"title": "Sleep", "duration": 480, "icon": eve[4]}, # 🛌
        ]
    return []

TEMPLATES = ["Morning", "Deep Work", "Study", "Evening"]
