# 🦆 Open Duck Mini Runtime

This repository contains the **Open Duck Mini Runtime** — a lightweight and modular runtime environment for small-scale biped/quadruped robot control and reinforcement learning deployment.

---

## 🎥 Demo Videos

| Preview | Description |
|----------|--------------|
| [▶️ Watch on YouTube](https://youtube.com/shorts/lvM5r-gL-LQ?feature=share) | Basic walking demo on real robot hardware |
| [▶️ Watch on YouTube](https://youtube.com/shorts/qtsCY4nndVE?feature=share) | Improved locomotion stability (v2 runtime) |

---

## 🖼️ Screenshot

<p align="center">
  <img src="https://github.com/user-attachments/assets/e5ea921e-6d63-4b25-a0d6-3734242110c2" width="75%" alt="Duck Mini Runtime UI Screenshot"/>
</p>

---

## 🧩 Key Features

- Modular runtime scripts for **Unitree-based robots**  
- Cross-platform Python support (Jetson / Raspberry Pi / PC)  
- Supports **ONNX** inference for walking controllers  
- Easy parameter customization via `duck_config.json`  
- Self-test and diagnostic scripts (`mini_bdx_selftest.py`)

---

## 🚀 Quick Start

```bash
git clone https://github.com/yitingHH-bit/Open_Duck_Mini_Runtime.git
cd Open_Duck_Mini_Runtime
python scripts/v2_rl_walk_mujoco.py
