import shutil
import os

src = r"C:\Users\adars\.gemini\antigravity\brain\629781dd-7f18-4eeb-8c6b-e19d1960caa0\logo_1767275209624.png"
dst = r"C:\Users\adars\MorningOS\assets\logo.png"

try:
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    print("Logo copied successfully.")
except Exception as e:
    print(f"Error copying logo: {e}")
