# Copyright (c) 2022-2025, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Common functions that can be used to activate certain terminations for the lift task.

The functions can be passed to the :class:`isaaclab.managers.TerminationTermCfg` object to enable
the termination introduced by the function.
"""

from __future__ import annotations

import torch
from typing import TYPE_CHECKING

from isaaclab.assets import Articulation, RigidObject
from isaaclab.managers import SceneEntityCfg

if TYPE_CHECKING:
    from isaaclab.envs import ManagerBasedRLEnv


def cubes_stacked(
    env: ManagerBasedRLEnv,
    robot_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
    cube_1_cfg: SceneEntityCfg = SceneEntityCfg("cube_1"),
    cube_2_cfg: SceneEntityCfg = SceneEntityCfg("cube_2"),
    cube_3_cfg: SceneEntityCfg = SceneEntityCfg("cube_3"),
    xy_threshold: float = 0.04,
    height_threshold: float = 0.005,
    height_diff: float = 0.0468,
    atol=0.0001,
    rtol=0.0001,
):
    robot: Articulation = env.scene[robot_cfg.name]
    cube_1: RigidObject = env.scene[cube_1_cfg.name]
    cube_2: RigidObject = env.scene[cube_2_cfg.name]
    cube_3: RigidObject = env.scene[cube_3_cfg.name]

    pos_diff_c12 = cube_1.data.root_pos_w - cube_2.data.root_pos_w
    pos_diff_c23 = cube_2.data.root_pos_w - cube_3.data.root_pos_w

    # Compute cube position difference in x-y plane
    xy_dist_c12 = torch.norm(pos_diff_c12[:, :2], dim=1)
    xy_dist_c23 = torch.norm(pos_diff_c23[:, :2], dim=1)

    # Compute cube height difference
    h_dist_c12 = torch.norm(pos_diff_c12[:, 2:], dim=1)
    h_dist_c23 = torch.norm(pos_diff_c23[:, 2:], dim=1)

    # Check cube positions
    stacked = torch.logical_and(xy_dist_c12 < xy_threshold, xy_dist_c23 < xy_threshold)
    stacked = torch.logical_and(h_dist_c12 - height_diff < height_threshold, stacked)
    stacked = torch.logical_and(pos_diff_c12[:, 2] < 0.0, stacked)
    stacked = torch.logical_and(h_dist_c23 - height_diff < height_threshold, stacked)
    stacked = torch.logical_and(pos_diff_c23[:, 2] < 0.0, stacked)

    # Check gripper positions
    if hasattr(env.scene, "surface_grippers") and len(env.scene.surface_grippers) > 0:
        surface_gripper = env.scene.surface_grippers["surface_gripper"]
        suction_cup_status = surface_gripper.state.view(-1, 1)  # 1: closed, 0: closing, -1: open
        suction_cup_is_open = (suction_cup_status == -1).to(torch.float32)
        stacked = torch.logical_and(suction_cup_is_open, stacked)

    else:
        if hasattr(env.cfg, "gripper_joint_names"):
            gripper_joint_ids, _ = robot.find_joints(env.cfg.gripper_joint_names)
            assert len(gripper_joint_ids) == 2, "Terminations only support parallel gripper for now"

            stacked = torch.logical_and(
                torch.isclose(
                    robot.data.joint_pos[:, gripper_joint_ids[0]],
                    torch.tensor(env.cfg.gripper_open_val, dtype=torch.float32).to(env.device),
                    atol=atol,
                    rtol=rtol,
                ),
                stacked,
            )
            stacked = torch.logical_and(
                torch.isclose(
                    robot.data.joint_pos[:, gripper_joint_ids[1]],
                    torch.tensor(env.cfg.gripper_open_val, dtype=torch.float32).to(env.device),
                    atol=atol,
                    rtol=rtol,
                ),
                stacked,
            )
        else:
            raise ValueError("No gripper_joint_names found in environment config")

    return stacked


def cubes_sorted(
    env: ManagerBasedRLEnv,
    robot_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
    cube_1_cfg: SceneEntityCfg = SceneEntityCfg("cube_1"),
    container_1_cfg: SceneEntityCfg = SceneEntityCfg("container_blue"),
    cube_2_cfg: SceneEntityCfg = SceneEntityCfg("cube_2"),
    container_2_cfg: SceneEntityCfg = SceneEntityCfg("container_red"),
    cube_3_cfg: SceneEntityCfg = SceneEntityCfg("cube_3"),
    container_3_cfg: SceneEntityCfg = SceneEntityCfg("container_green"),
    xy_threshold: float = 0.06,
    max_height: float = 0.06,
    atol: float = 0.0001,
    rtol: float = 0.0001,
) -> torch.Tensor:
    """Termination signal for the cube sorting task.

    Returns True for environments where every cube is resting on top of its matching colored
    container (XY close to the container center, near the container surface) and the gripper is
    open (i.e. all cubes have been released).
    """
    robot: Articulation = env.scene[robot_cfg.name]

    pairs = [
        (cube_1_cfg, container_1_cfg),
        (cube_2_cfg, container_2_cfg),
        (cube_3_cfg, container_3_cfg),
    ]

    sorted_mask = torch.ones(env.num_envs, dtype=torch.bool, device=env.device)
    for cube_cfg, container_cfg in pairs:
        cube: RigidObject = env.scene[cube_cfg.name]
        container: RigidObject = env.scene[container_cfg.name]

        pos_diff = cube.data.root_pos_w - container.data.root_pos_w
        xy_dist = torch.norm(pos_diff[:, :2], dim=1)
        height_dist = torch.abs(pos_diff[:, 2])

        sorted_mask = torch.logical_and(sorted_mask, xy_dist < xy_threshold)
        sorted_mask = torch.logical_and(sorted_mask, height_dist < max_height)

    # Check gripper is open (all cubes released)
    if hasattr(env.cfg, "gripper_joint_names"):
        gripper_joint_ids, _ = robot.find_joints(env.cfg.gripper_joint_names)
        assert len(gripper_joint_ids) == 2, "Terminations only support parallel gripper for now"

        for joint_id in gripper_joint_ids:
            sorted_mask = torch.logical_and(
                torch.isclose(
                    robot.data.joint_pos[:, joint_id],
                    torch.tensor(env.cfg.gripper_open_val, dtype=torch.float32).to(env.device),
                    atol=atol,
                    rtol=rtol,
                ),
                sorted_mask,
            )
    else:
        raise ValueError("No gripper_joint_names found in environment config")

    return sorted_mask
