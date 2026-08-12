from __future__ import annotations

import subprocess
import sys


CONFIGS = [
    "configs/norman_gears_L0_seed1.yaml",
    "configs/norman_gears_L1_seed1.yaml",
    "configs/norman_gears_L2_seed1.yaml",
]


def main():
    for cfg in CONFIGS:
        subprocess.run([sys.executable, "-m", "src.run", "--config", cfg], check=True)


if __name__ == "__main__":
    main()

