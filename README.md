<div align="center">

<img src="assets/screenshots/home.png" alt="InFlow Logo" width="120" height="auto" />

# MorningOS (InFlow)
**Your Flow State, Engineered.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg?style=for-the-badge)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

*An adaptive, session-based productivity environment designed to minimize cognitive friction and orchestrate deep work.*

[Features](#-core-features) • [Installation](#-installation--setup) • [Architecture](#-architecture) • [Contributing](#-contributing)

<br />
<img src="assets/screenshots/home.png" alt="InFlow Home Screen" width="100%" style="border-radius: 8px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
<br />
</div>

---

## 🌊 Philosophy

In a world governed by infinite feeds and constant context-switching, MorningOS (InFlow) provides a sanctuary for focused execution. Unlike traditional calendar applications that manage time as a scarce resource, MorningOS visualizes time as a **stream of focus**.

By enforcing strict, modular "Sessions" within a dedicated, distraction-free desktop environment, MorningOS helps you define intent, enter the zone consistently, and maintain rhythm throughout your workday.

---

## ✨ Core Features

### 🎯 Session-Based Execution
Build your routine using modular time-blocks. Transition seamlessly between deep work, meditation, and breaks without breaking state.
* **Fluid Reordering**: Drag and drop session blocks to adapt your schedule dynamically.
* **Active Focus Mode**: A dedicated, full-screen timer view minimizes desktop clutter and anchors your attention.
* **Granular Control**: Pause, resume, or restart specific blocks effortlessly.

### 📊 Insightful Analytics
Track your productivity patterns with an integrated, privacy-focused local database.
* **Real-time Metrics**: Monitor total focus time, session completion rates, and daily streaks.
* **7-Day Trend Visualization**: Custom-built, interactive charts render your weekly activity to highlight momentum and identify friction points.

### 🎨 Adaptive, Glassmorphism UI
Your environment dictates your mindset. MorningOS features a bespoke rendering engine utilizing high-performance Tkinter Canvas operations to achieve modern, web-like aesthetics natively.
* **OLED-Ready Themes**: From *Carbon* to *Cyberpunk*, select deep-contrast themes tailored for visual comfort.
* **Fluid Micro-interactions**: Hover states, tooltips, and dynamic layouts respond instantly to user input.

### ☁️ Seamless Cloud Synchronization
Keep your routines backed up and synchronized across devices without the overhead of heavy backend frameworks.
* **Supabase Integration**: Direct REST API integration securely pulls and pushes your SQLite data to the cloud.

---

## 🚀 Installation & Setup

### Prerequisites
* Python 3.10 or higher
* Git

### Local Deployment
```bash
# 1. Clone the repository
git clone https://github.com/getsauce-in/InFlow.git
cd InFlow

# 2. Install minimal dependencies
pip install -r requirements.txt
```

### Quick Launch
MorningOS is designed to be lightweight. We have provided packaged launch scripts so you never need to touch the terminal after installation:

* **Windows**: Double-click the provided `run.bat` script. *(Tip: Pin this script to your taskbar and set its icon to `assets/screenshots/home.png` for a native application feel!)*
* **macOS / Linux**: Execute `./run.sh` from your terminal or bind it to an application launcher.
* **Manual execution**: `python main.py`

---

## 🏗 Architecture

MorningOS is engineered for absolute reliability and low resource consumption, bridging the gap between hardware-level execution and modern UI paradigms.

* **Frontend**: Pure Python `Tkinter`. We bypass standard, rigid OS widgets by rendering bespoke `Canvas` objects (e.g., `RoundedRect`, `GlassCard`, `NeonButton`) to achieve hardware-accelerated, customizable aesthetics without the footprint of Electron or Chromium.
* **State Management**: Event-driven UI updates bound tightly to a localized `BlocksManager`.
* **Persistence**: Python's native `sqlite3` ensures atomic, zero-configuration local storage.
* **Networking**: Non-blocking `httpx` routines handle explicit cloud synchronization payloads to Supabase endpoints, guaranteeing offline-first capability.

---

## 🤝 Contributing

We are committed to building an open, highly-performant ecosystem for productivity. Contributions from developers, designers, and productivity researchers are highly encouraged.

1. **Fork** the repository
2. **Create** your feature branch: `git checkout -b feature/AmazingImplementation`
3. **Commit** your changes: `git commit -m 'feat: Add sophisticated algorithm'`
4. **Push** to the branch: `git push origin feature/AmazingImplementation`
5. **Open** a Pull Request

---

<div align="center">
    <i>Engineered with precision by the <a href="https://github.com/getsauce-in">InFlow Team</a>.</i>
</div>
