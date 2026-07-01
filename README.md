# Isaac Lab Cube Sort Task

Custom Franka cube sorting task for NVIDIA Isaac Lab 2.3.1 and Isaac Lab Mimic.

This project builds a Franka robot arm and cube sorting environment in Isaac Sim
and Isaac Lab. The full workflow starts from 10 keyboard-controlled human
demonstration trajectories, uses Isaac Lab Mimic for GR00T-Mimic-style subtask
annotation and trajectory generation, expands the data to about 1,000 synthetic
trajectories, and trains a BC-RNN-GMM imitation-learning policy for the cube
sorting task.

## Demo

https://github.com/user-attachments/assets/c74d84f5-29e5-496e-8775-abef5579f925


## Included

- Isaac Lab task overlay files for:
  - `Isaac-Sort-Cube-Franka-v0`
  - `Isaac-Sort-Cube-Franka-IK-Rel-v0`
  - `Isaac-Sort-Cube-Franka-IK-Rel-Mimic-v0`
- Mimic subtask configuration for three grasp/place pairs.
- Small verification scripts in `tools/`.

## Project Structure

```text
.
├── assets/
│   └── cube_sort_demo.mp4
├── isaaclab_overlay/
│   └── source/
│       ├── isaaclab_tasks/
│       └── isaaclab_mimic/
├── scripts/
│   └── install_overlay.sh
├── tools/
│   ├── gui_view_sort.py
│   ├── verify_sort_mimic.py
│   └── verify_sort_scene.py
├── LICENSE
├── LICENSES/
├── NOTICE.md
└── README.md
```

- `isaaclab_overlay/` contains files copied over an Isaac Lab installation.
- `tools/` contains basic environment and Mimic verification scripts.
- `assets/` contains lightweight media used by this README.
- `scripts/install_overlay.sh` installs the overlay into a target Isaac Lab
  root.
- `LICENSES/` contains upstream BSD-3-Clause and Apache-2.0 license texts.

## Not Included

This repository intentionally excludes datasets, generated demonstrations,
training logs, model checkpoints, NVIDIA GTC/DLI lab instruction files, fonts,
and other binary artifacts from the original local workspace.

## Requirements

- NVIDIA Isaac Sim 5.1.0 and Isaac Lab 2.3.1
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

## Imitation Learning Workflow

The full training workflow is not included as runnable data in this repository,
but it follows the Isaac Lab teleoperation, Isaac Lab Mimic, and RoboMimic
pipeline below.

### 1. Collect Demonstrations

Record keyboard teleoperation demonstrations for the sorting task:

```bash
cd ~/IsaacLab
./isaaclab.sh -p scripts/tools/record_demos.py \
  --task Isaac-Sort-Cube-Franka-IK-Rel-v0 \
  --teleop_device keyboard \
  --device cuda \
  --dataset_file /path/to/datasets/sort_dataset_keyboard.hdf5 \
  --num_demos 10
```

Keyboard controls:

- `W` / `S`: move end-effector along x
- `A` / `D`: move end-effector along y
- `Q` / `E`: move end-effector along z
- `K`: open or close the gripper
- `R`: reset and discard the current episode

### 2. Annotate Demonstrations

Use the Mimic task wrapper to annotate grasp/place subtasks:

```bash
./isaaclab.sh -p scripts/imitation_learning/isaaclab_mimic/annotate_demos.py \
  --input_file /path/to/datasets/sort_dataset_keyboard.hdf5 \
  --output_file /path/to/datasets/sort_annotated_keyboard.hdf5 \
  --task Isaac-Sort-Cube-Franka-IK-Rel-Mimic-v0 \
  --auto
```

### 3. Generate Synthetic Trajectories

Expand the annotated demonstrations into a larger synthetic dataset:

```bash
./isaaclab.sh -p scripts/imitation_learning/isaaclab_mimic/generate_dataset.py \
  --input_file /path/to/datasets/sort_annotated_keyboard.hdf5 \
  --output_file /path/to/datasets/sort_generated.hdf5 \
  --num_envs 400 \
  --generation_num_trials 1000 \
  --headless
```

### 4. Train a Policy

Train a RoboMimic BC-RNN-GMM policy:

```bash
./isaaclab.sh -p scripts/imitation_learning/robomimic/train.py \
  --task Isaac-Sort-Cube-Franka-IK-Rel-v0 \
  --algo bc \
  --dataset /path/to/datasets/sort_generated.hdf5 \
  --log_dir /path/to/training_logs
```

### 5. Play a Trained Policy

Run the trained checkpoint in simulation:

```bash
./isaaclab.sh -p scripts/imitation_learning/robomimic/play.py \
  --task Isaac-Sort-Cube-Franka-IK-Rel-v0 \
  --num_rollouts 20 \
  --horizon 1800 \
  --checkpoint /path/to/training_logs/.../models/model_epoch_XXXX.pth \
  --seed 100
```

## Testing Scope

This repository has been tested only for basic task loading and Isaac Lab Mimic
wiring.

Full imitation-learning reproduction is intentionally out of scope for this
repository because demonstration datasets, generated datasets, training logs,
and trained checkpoints are not included. To reproduce training, collect or
provide your own demonstration dataset and run the Isaac Lab Mimic and RoboMimic
pipeline separately.

## Maintainer

Maintained by Vincent.

This project adapts NVIDIA Isaac Lab and Isaac Lab Mimic examples for a custom
Franka cube sorting task.

If you need a Mandarin tutorial, here is a link for you:
https://medium.com/p/d5fdf18f545e?postPublishedType=initial

## Acknowledgements

This project is based on NVIDIA Isaac Lab and Isaac Lab Mimic.

## License

This is a mixed-license repository:

- Isaac Lab-derived files under `isaaclab_overlay/source/isaaclab_tasks/` are
  licensed under BSD-3-Clause.
- Isaac Lab Mimic-derived files under `isaaclab_overlay/source/isaaclab_mimic/`
  are licensed under Apache-2.0.
- Repository documentation and helper scripts are licensed under Apache-2.0
  unless stated otherwise.

See `LICENSE`, `LICENSES/`, and `NOTICE.md`.
