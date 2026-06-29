# Open the Cube Sort scene in the Isaac Sim GUI so the layout can be inspected visually.
#
# The window opens on the user's monitor. The arm holds still (zero action); cubes settle and
# the scene auto-resets each time an episode ends, so the randomized cube layout keeps refreshing.
#
# SPDX-License-Identifier: Apache-2.0

import argparse
import os
from pathlib import Path

from isaaclab.app import AppLauncher

DEFAULT_REPORT_DIR = Path(__file__).resolve().parents[1] / "reports"
STATUS = os.environ.get("SORT_GUI_STATUS", str(DEFAULT_REPORT_DIR / "sort_gui_status.txt"))

parser = argparse.ArgumentParser()
parser.add_argument("--task", type=str, default="Isaac-Sort-Cube-Franka-IK-Rel-v0")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
args.headless = False  # GUI window on the user's screen

app_launcher = AppLauncher(args)
simulation_app = app_launcher.app

import torch

import gymnasium as gym
import isaaclab_tasks  # noqa: F401
from isaaclab_tasks.utils import parse_env_cfg

Path(STATUS).parent.mkdir(parents=True, exist_ok=True)
_s = open(STATUS, "w")


def status(msg):
    _s.write(msg + "\n")
    _s.flush()


def main():
    status(f"loading task {args.task} ...")
    env_cfg = parse_env_cfg(args.task, device=args.device, num_envs=1)
    env = gym.make(args.task, cfg=env_cfg)
    env.reset()

    # Frame the table workspace nicely from an angled 3D view.
    env.unwrapped.sim.set_camera_view(eye=(1.4, -1.1, 1.0), target=(0.5, 0.0, 0.05))

    n_act = env.unwrapped.action_manager.total_action_dim
    zero_action = torch.zeros((env.unwrapped.num_envs, n_act), device=env.unwrapped.device)
    status("GUI READY - scene loaded, window should be visible. Orbit with the mouse to inspect.")

    while simulation_app.is_running():
        obs, rew, terminated, truncated, info = env.step(zero_action)
        if bool(terminated.any()) or bool(truncated.any()):
            env.reset()

    env.close()


try:
    main()
finally:
    _s.flush()
    _s.close()
    simulation_app.close()
