#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 /path/to/isaaclab/root"
  echo
  echo "Example:"
  echo "  $0 ~/env_isaacsim/lib/python3.11/site-packages/isaaclab"
  exit 1
fi

TARGET_ROOT="${1%/}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
OVERLAY_DIR="$REPO_ROOT/isaaclab_overlay"

if [[ ! -d "$TARGET_ROOT/source" ]]; then
  echo "Error: target does not contain a source/ directory: $TARGET_ROOT"
  exit 1
fi

cp -a "$OVERLAY_DIR/." "$TARGET_ROOT/"

echo "Installed overlay into: $TARGET_ROOT"
