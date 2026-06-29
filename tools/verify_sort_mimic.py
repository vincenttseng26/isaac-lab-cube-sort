# Verify the Cube Sort *Mimic* environment loads and is wired correctly for annotation/generation.
# Writes a report (flushed) so it survives Isaac Sim's hard-exit.
#
# SPDX-License-Identifier: Apache-2.0

import argparse
import os
from pathlib import Path

from isaaclab.app import AppLauncher

DEFAULT_REPORT_DIR = Path(__file__).resolve().parents[1] / "reports"
REPORT = os.environ.get("SORT_MIMIC_REPORT", str(DEFAULT_REPORT_DIR / "sort_mimic_report.txt"))

parser = argparse.ArgumentParser()
parser.add_argument("--task", type=str, default="Isaac-Sort-Cube-Franka-IK-Rel-Mimic-v0")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
args.headless = True

app_launcher = AppLauncher(args)
simulation_app = app_launcher.app

import traceback

import gymnasium as gym
import isaaclab_mimic.envs  # noqa: F401  (registers the mimic tasks)
import isaaclab_tasks  # noqa: F401
from isaaclab_tasks.utils import parse_env_cfg

Path(REPORT).parent.mkdir(parents=True, exist_ok=True)
_f = open(REPORT, "w")


def log(m=""):
    _f.write(str(m) + "\n")
    _f.flush()


def main():
    log(f"task = {args.task}")
    env_cfg = parse_env_cfg(args.task, device=args.device, num_envs=1)
    env = gym.make(args.task, cfg=env_cfg)
    log("mimic env created OK")
    env.reset()

    # 1. Subtask configs
    sc = env.unwrapped.cfg.subtask_configs["franka"]
    log(f"\nsubtask_configs count = {len(sc)} (expect 6)")
    for i, s in enumerate(sc):
        log(f"  [{i}] object_ref={s.object_ref:16s} term_signal={s.subtask_term_signal}")

    # 2. subtask_terms obs group keys
    st = env.unwrapped.obs_buf["subtask_terms"]
    log(f"\nobs subtask_terms keys = {sorted(st.keys())}")

    # 3. get_subtask_term_signals (used by annotate_demos --auto)
    sig = env.unwrapped.get_subtask_term_signals()
    log(f"get_subtask_term_signals keys = {sorted(sig.keys())} (expect grasp_1/2/3, place_1/2)")

    # 4. object poses available to mimic (must include containers for place subtasks)
    poses = env.unwrapped.get_object_poses()
    log(f"\nget_object_poses keys = {sorted(poses.keys())}")
    missing = [s.object_ref for s in sc if s.object_ref not in poses]
    log(f"object_ref missing from poses = {missing} (expect [])")

    log("\n[DONE] mimic env verified")
    env.close()


try:
    main()
except Exception:
    log("\n[ERROR]\n" + traceback.format_exc())
finally:
    _f.flush()
    _f.close()
    simulation_app.close()
