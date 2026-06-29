# Verify the Cube Sort scene by actually loading it headless.
#
# Writes REAL world coordinates (not guesses) to a results file with explicit flush, so the
# data survives even though Isaac Sim hard-exits (os._exit) on close and discards stdout buffers.
# Also renders a top-down screenshot for visual inspection.
#
# SPDX-License-Identifier: Apache-2.0

import argparse
import os
from pathlib import Path

from isaaclab.app import AppLauncher

DEFAULT_REPORT_DIR = Path(__file__).resolve().parents[1] / "reports"
RESULTS = os.environ.get("SORT_SCENE_REPORT", str(DEFAULT_REPORT_DIR / "sort_scene_report.txt"))

parser = argparse.ArgumentParser()
parser.add_argument("--task", type=str, default="Isaac-Sort-Cube-Franka-IK-Rel-v0")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
args.headless = True
args.enable_cameras = True

app_launcher = AppLauncher(args)
simulation_app = app_launcher.app

import traceback

import numpy as np
import torch

import gymnasium as gym
import isaaclab_tasks  # noqa: F401  (registers the tasks)
from isaaclab_tasks.utils import parse_env_cfg

Path(RESULTS).parent.mkdir(parents=True, exist_ok=True)
_f = open(RESULTS, "w")


def log(msg=""):
    _f.write(str(msg) + "\n")
    _f.flush()


def fmt(t):
    return np.array2string(t.detach().cpu().numpy().reshape(-1), precision=4, suppress_small=True)


def main():
    log(f"task = {args.task}")
    env_cfg = parse_env_cfg(args.task, device=args.device, num_envs=1)
    env = gym.make(args.task, cfg=env_cfg)
    log("env created OK")

    env.reset()
    scene = env.unwrapped.scene
    env_origin = scene.env_origins[0]

    log("\n===== COORDS RIGHT AFTER RESET (world frame) =====")
    log(f"env_origin = {fmt(env_origin)}")
    names = ["cube_1", "cube_2", "cube_3", "container_blue", "container_red", "container_green"]
    for name in names:
        pos = scene[name].data.root_pos_w[0]
        log(f"{name:16s} world={fmt(pos)}  rel={fmt(pos - env_origin)}")
    ee = scene["ee_frame"].data.target_pos_w[0, 0, :]
    log(f"{'ee_frame':16s} world={fmt(ee)}  rel={fmt(ee - env_origin)}")
    robot_base = scene["robot"].data.root_pos_w[0]
    log(f"{'robot_base':16s} world={fmt(robot_base)}")

    log("\n-- horizontal dist robot_base -> container (Franka reach ~0.85 m) --")
    for name in ["container_blue", "container_red", "container_green"]:
        d = torch.norm((scene[name].data.root_pos_w[0] - robot_base)[:2]).item()
        log(f"  {name:16s} dist_xy = {d:.3f} m")

    # Step physics so cubes settle (reveals true table-top height).
    n_act = env.unwrapped.action_manager.total_action_dim
    zero_action = torch.zeros((env.unwrapped.num_envs, n_act), device=env.unwrapped.device)
    for _ in range(60):
        env.step(zero_action)

    log("\n===== AFTER 60 SETTLING STEPS =====")
    for name in names:
        pos = scene[name].data.root_pos_w[0]
        log(f"{name:16s} world={fmt(pos)}  rel={fmt(pos - env_origin)}")
    log("\n-- settled cube z (reveals real table-top height) --")
    for name in ["cube_1", "cube_2", "cube_3"]:
        log(f"  {name:16s} z = {scene[name].data.root_pos_w[0, 2].item():.4f}")

    # Top-down render via a standalone replicator camera + BasicWriter (different code path
    # than env.render(), which hits a syntheticdata bug in this Isaac Sim build).
    out_dir = os.environ.get("SORT_SCENE_SHOT_DIR", str(DEFAULT_REPORT_DIR / "sort_scene_shots"))
    os.makedirs(out_dir, exist_ok=True)
    try:
        import omni.replicator.core as rep

        # Top-down camera looking straight down at the table workspace center.
        top_cam = rep.create.camera(position=(0.5, 0.0, 1.3), look_at=(0.5, 0.0, 0.0))
        # Angled camera for a 3D perspective view.
        persp_cam = rep.create.camera(position=(1.25, -0.9, 0.9), look_at=(0.5, 0.0, 0.05))
        rp_top = rep.create.render_product(top_cam, (1024, 1024))
        rp_persp = rep.create.render_product(persp_cam, (1280, 960))

        writer = rep.WriterRegistry.get("BasicWriter")
        writer.initialize(output_dir=out_dir, rgb=True)
        writer.attach([rp_top, rp_persp])

        for _ in range(12):
            rep.orchestrator.step(rt_subframes=8)
        rep.orchestrator.wait_until_complete()
        log(f"\n[OK] replicator wrote frames to {out_dir}")
        log("  files: " + ", ".join(sorted(os.listdir(out_dir))))
    except Exception:
        log("\n[WARN] replicator screenshot failed:\n" + traceback.format_exc())

    log("\n[DONE]")
    env.close()


try:
    main()
except Exception:
    log("\n[ERROR] exception in main:\n" + traceback.format_exc())
finally:
    _f.flush()
    _f.close()
    simulation_app.close()
