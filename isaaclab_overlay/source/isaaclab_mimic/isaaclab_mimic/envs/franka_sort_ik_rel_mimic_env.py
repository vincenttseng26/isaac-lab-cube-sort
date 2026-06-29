# Copyright (c) 2024-2025, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Sequence

import torch

from .franka_stack_ik_rel_mimic_env import FrankaCubeStackIKRelMimicEnv


class FrankaCubeSortIKRelMimicEnv(FrankaCubeStackIKRelMimicEnv):
    """Isaac Lab Mimic environment wrapper for the Franka cube *sorting* task.

    Re-uses the Franka IK-Rel end-effector / action helpers from the stacking Mimic env, and only
    overrides the subtask termination signals so that automatic annotation (``annotate_demos --auto``)
    covers the three grasp/place pairs of the sorting task.
    """

    def get_subtask_term_signals(self, env_ids: Sequence[int] | None = None) -> dict[str, torch.Tensor]:
        """Termination signals for the six sorting subtasks.

        Subtask order: grasp cube_1 -> place on blue, grasp cube_2 -> place on red,
        grasp cube_3 -> place on green. The final place subtask end does not need a signal.
        """
        if env_ids is None:
            env_ids = slice(None)

        signals = dict()
        subtask_terms = self.obs_buf["subtask_terms"]
        signals["grasp_1"] = subtask_terms["grasp_1"][env_ids]
        signals["place_1"] = subtask_terms["place_1"][env_ids]
        signals["grasp_2"] = subtask_terms["grasp_2"][env_ids]
        signals["place_2"] = subtask_terms["place_2"][env_ids]
        signals["grasp_3"] = subtask_terms["grasp_3"][env_ids]
        # final subtask (place cube_3 on the green platform) end signal is not needed
        return signals
