# Copyright (c) 2024-2025, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0

from isaaclab.envs.mimic_env_cfg import MimicEnvCfg, SubTaskConfig
from isaaclab.utils import configclass

from isaaclab_tasks.manager_based.manipulation.stack.config.franka.sort_ik_rel_env_cfg import FrankaCubeSortEnvCfg


@configclass
class FrankaCubeSortIKRelMimicEnvCfg(FrankaCubeSortEnvCfg, MimicEnvCfg):
    """
    Isaac Lab Mimic environment config class for the Franka Cube Sort IK Rel env.

    The task is decomposed into three object-centric grasp/place pairs. Each grasp subtask is
    referenced to the cube being picked up; each place subtask is referenced to the fixed colored
    platform the cube should be sorted onto:
        grasp cube_1 -> place on container_blue
        grasp cube_2 -> place on container_red
        grasp cube_3 -> place on container_green
    """

    def __post_init__(self):
        # post init of parents
        super().__post_init__()

        # Datagen configuration
        self.datagen_config.name = "demo_src_sort_isaac_lab_task_D0"
        self.datagen_config.generation_guarantee = True
        self.datagen_config.generation_keep_failed = True
        self.datagen_config.generation_num_trials = 10
        self.datagen_config.generation_select_src_per_subtask = True
        self.datagen_config.generation_transform_first_robot_pose = False
        self.datagen_config.generation_interpolate_from_last_target_pose = True
        self.datagen_config.generation_relative = True
        self.datagen_config.max_num_failures = 25
        self.datagen_config.seed = 1

        common = dict(
            subtask_term_offset_range=(10, 20),
            selection_strategy="nearest_neighbor_object",
            selection_strategy_kwargs={"nn_k": 3},
            action_noise=0.03,
            num_interpolation_steps=5,
            num_fixed_steps=0,
            apply_noise_during_interpolation=False,
        )

        subtask_configs = []
        # 1. Grasp the blue cube
        subtask_configs.append(
            SubTaskConfig(
                object_ref="cube_1",
                subtask_term_signal="grasp_1",
                description="Grasp blue cube",
                next_subtask_description="Place blue cube on the blue platform",
                **common,
            )
        )
        # 2. Place the blue cube on the blue platform
        subtask_configs.append(
            SubTaskConfig(
                object_ref="container_blue",
                subtask_term_signal="place_1",
                description="Place blue cube on the blue platform",
                next_subtask_description="Grasp red cube",
                **common,
            )
        )
        # 3. Grasp the red cube
        subtask_configs.append(
            SubTaskConfig(
                object_ref="cube_2",
                subtask_term_signal="grasp_2",
                description="Grasp red cube",
                next_subtask_description="Place red cube on the red platform",
                **common,
            )
        )
        # 4. Place the red cube on the red platform
        subtask_configs.append(
            SubTaskConfig(
                object_ref="container_red",
                subtask_term_signal="place_2",
                description="Place red cube on the red platform",
                next_subtask_description="Grasp green cube",
                **common,
            )
        )
        # 5. Grasp the green cube
        subtask_configs.append(
            SubTaskConfig(
                object_ref="cube_3",
                subtask_term_signal="grasp_3",
                description="Grasp green cube",
                next_subtask_description="Place green cube on the green platform",
                **common,
            )
        )
        # 6. Place the green cube on the green platform (final subtask: end not detected)
        subtask_configs.append(
            SubTaskConfig(
                object_ref="container_green",
                subtask_term_signal=None,
                subtask_term_offset_range=(0, 0),
                selection_strategy="nearest_neighbor_object",
                selection_strategy_kwargs={"nn_k": 3},
                action_noise=0.03,
                num_interpolation_steps=5,
                num_fixed_steps=0,
                apply_noise_during_interpolation=False,
                description="Place green cube on the green platform",
            )
        )
        self.subtask_configs["franka"] = subtask_configs
