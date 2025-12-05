# 🦆 Open Duck Mini Runtime

This repository contains the **Open Duck Mini Runtime** — a lightweight and modular runtime environment for small-scale biped/quadruped robot control and reinforcement learning deployment.

---
# 🦆  student project/replica  project (studying savonia UAS )

| Role | Name | Responsibility |
|------|------|----------------|

| **Supervisor** | **Markku K. ** | Academic supervision and technical guidance |
| **Group Manager** | **Jiancai H** | System integration, reinforcement learning runtime, documentation |
| **Software Developer** | **Danila M.** | Python runtime logic, controller scripts, communication modules |
| **Hardware Assembler** | **Agozie J O.** | Physical robot setup, sensor calibration, wiring |

## 🎥 Demo Videos

| Preview | Description |
|----------|--------------|
| [▶️ Watch on YouTube](https://youtube.com/shorts/lvM5r-gL-LQ?feature=share) | Basic walking demo on real robot hardware |
| [▶️ Watch on YouTube](https://youtube.com/shorts/qtsCY4nndVE?feature=share) | Improved locomotion stability (v2 runtime) |

---

##  display

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

## hard ware part 

From the DataSheet @ https://www.ti.com/product/TLVM13610?keyMatch=tlvm13610rdfr&tisearch=universal_search   and the circuit can be found here https://www.ti.com/lit/ds/symlink/tlvm13610.pdf?ts=1762995465366. 
<img width="1897" height="880" alt="image" src="https://github.com/user-attachments/assets/86a23cfe-6d99-4a03-88d7-7d5d68d2276a" />
<img width="790" height="495" alt="image" src="https://github.com/user-attachments/assets/1a911248-7f5c-4aba-b3bd-05f14d650cd0" />



