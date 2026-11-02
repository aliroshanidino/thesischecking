#!/usr/bin/env bash
# Push the current branch to the bare repo on the HPC; the post-receive hook checks it out into src/.
# Usage: tools/push.sh
set -euo pipefail
source "$(dirname "$0")/hpc.env"
cd "$(git rev-parse --show-toplevel)"
branch=$(git rev-parse --abbrev-ref HEAD)
if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
  echo "warning: uncommitted changes are NOT pushed" >&2
fi
git push hpc "$branch"
echo "HPC src is now at: $(ssh -o BatchMode=yes "$HPC" "git --git-dir=$HPC_ROOT/repo.git rev-parse --short refs/heads/$branch")  (local HEAD $(git rev-parse --short HEAD))"
