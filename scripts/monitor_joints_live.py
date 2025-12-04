#!/usr/bin/env python3
"""
实时显示 Duck 机器人各关节当前角度（单位：度）
按 Ctrl+C 退出
"""

import time
import numpy as np

from mini_bdx_runtime.rustypot_position_hwi import HWI
from mini_bdx_runtime.duck_config import DuckConfig


def main():
    # 这里用 dummy_config，和你标定脚本一样的写法
    dummy_config = DuckConfig(config_json_path=None, ignore_default=True)
    hwi = HWI(dummy_config)

    # 如果此时电机已经在其他程序里 turn_on 过，可以把下面两行注释掉
    print("Initializing (set zero pos & low torque)...")
    hwi.init_pos = hwi.zero_pos
    hwi.set_kds([0] * len(hwi.joints))
    hwi.turn_on()
    time.sleep(0.5)

    print("Live joint monitor started. Press Ctrl+C to stop.")

    try:
        while True:
            # 读取当前关节角度（rad，已经减掉 offset）
            positions_rad = hwi.get_present_positions()
            if positions_rad is None:
                continue

            positions_deg = np.rad2deg(positions_rad)

            # 清屏 + 光标回到左上角（只在支持 ANSI 的终端有效）
            print("\033[2J\033[H", end="")

            print("=== Live joint positions (degrees) ===")
            for name, deg in zip(hwi.joints.keys(), positions_deg):
                print(f"{name:>15}: {deg: 7.2f} °")
            print("======================================")

            # 刷新间隔（秒），可根据需要调整
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nStopped monitoring.")
        # 调试时一般不强制关电机，你可以自己决定要不要 turn_off
        # hwi.turn_off()


if __name__ == "__main__":
    main()
