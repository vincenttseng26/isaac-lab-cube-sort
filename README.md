# Isaac Lab Cube Sort Task

Custom Franka cube sorting task for NVIDIA Isaac Lab 2.3.1 and Isaac Lab Mimic.

The task extends the Isaac Lab cube stacking examples into a color sorting
workflow: three cubes are spawned on the table and the robot places each cube on
its matching fixed platform.

## Included

- Isaac Lab task overlay files for:
  - `Isaac-Sort-Cube-Franka-v0`
  - `Isaac-Sort-Cube-Franka-IK-Rel-v0`
  - `Isaac-Sort-Cube-Franka-IK-Rel-Mimic-v0`
- Mimic subtask configuration for three grasp/place pairs.
- Small verification scripts in `tools/`.

## Not Included

This repository intentionally excludes datasets, generated demonstrations,
training logs, model checkpoints, NVIDIA GTC/DLI lab instruction files, fonts,
and other binary artifacts from the original local workspace.

## Requirements

- NVIDIA Isaac Sim and Isaac Lab 2.3.1
- A working Isaac Lab Python environment
- Isaac Lab Mimic dependencies for annotation/data generation
- RoboMimic if you plan to train or play policies

The files were developed against the Isaac Lab pip installation layout where the
target root looks like:

```bash
~/env_isaacsim/lib/python3.11/site-packages/isaaclab
```

## Install Overlay

From this repository:

```bash
./scripts/install_overlay.sh ~/env_isaacsim/lib/python3.11/site-packages/isaaclab
```

The script copies `isaaclab_overlay/source/` into the target Isaac Lab root.
Pass a different target if your Isaac Lab checkout or package is elsewhere, as
long as the target contains a `source/` directory.

## Verify

Activate your Isaac Lab environment, then run:

```bash
cd ~/IsaacLab
./isaaclab.sh -p /path/to/this/repo/tools/verify_sort_scene.py --device cuda
./isaaclab.sh -p /path/to/this/repo/tools/verify_sort_mimic.py --device cuda
```

Reports are written to `reports/` by default. You can inspect the scene with:

```bash
./isaaclab.sh -p /path/to/this/repo/tools/gui_view_sort.py --device cuda
```

## License

This is a mixed-license repository:

- Isaac Lab-derived files under `isaaclab_overlay/source/isaaclab_tasks/` are
  licensed under BSD-3-Clause.
- Isaac Lab Mimic-derived files under `isaaclab_overlay/source/isaaclab_mimic/`
  are licensed under Apache-2.0.
- Repository documentation and helper scripts are licensed under Apache-2.0
  unless stated otherwise.

See `LICENSE`, `LICENSES/`, and `NOTICE.md`.
