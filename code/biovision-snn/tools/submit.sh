#!/usr/bin/env bash
# Start a detached job on the HPC in tmux; it survives a dropped SSH connection.
# Usage: tools/submit.sh <name> <threads> <cmd...>
#   e.g. tools/submit.sh s1_stdp 8 python -m biovision.experiments.phase0 --config configs/phase0_caltech.yaml
# Creates runs/<phase>/<YYYYmmdd-HHMM>_<name>/ with cmd.txt, git_commit.txt, threads, run.sh, pid,
# log.txt and exit_code (when finished). <phase> comes from the branch (phase-0 -> phase0, else branch name).
# The experiment itself writes config.yaml, metrics.json and figs/ into $RUN_DIR.
set -euo pipefail
source "$(dirname "$0")/hpc.env"
[ $# -ge 3 ] || { echo "usage: $0 <name> <threads> <cmd...>" >&2; exit 2; }
name=$1; threads=$2; shift 2; cmd="$*"
[[ "$name" =~ ^[A-Za-z0-9_.-]+$ ]] || { echo "name must match [A-Za-z0-9_.-]+" >&2; exit 2; }
[[ "$threads" =~ ^[0-9]+$ ]] && [ "$threads" -ge 1 ] && [ "$threads" -le "$MAX_THREADS" ] \
  || { echo "threads must be 1..$MAX_THREADS" >&2; exit 2; }

cd "$(git rev-parse --show-toplevel)"
branch=$(git rev-parse --abbrev-ref HEAD)
case "$branch" in phase-*) phase="phase${branch#phase-}" ;; *) phase="$branch" ;; esac

# Reproducibility: the HPC must run exactly the local HEAD.
local_head=$(git rev-parse HEAD)
remote_head=$(ssh -o BatchMode=yes "$HPC" "git --git-dir=$HPC_ROOT/repo.git rev-parse refs/heads/$branch 2>/dev/null || echo none")
if [ "$local_head" != "$remote_head" ] && [ "${FORCE:-0}" != 1 ]; then
  echo "HPC has $remote_head but local HEAD is $local_head: commit + tools/push.sh first (or FORCE=1)." >&2
  exit 1
fi
[ -z "$(git status --porcelain --untracked-files=no)" ] || echo "warning: uncommitted local changes are not part of this run" >&2

# Thread budget across our running jobs (shared machine, DECISIONS D1).
used=$(ssh -o BatchMode=yes "$HPC" bash -s -- "$HPC_ROOT" <<'EOF'
s=0
for f in "$1"/runs/*/*/threads; do
  [ -f "$f" ] || continue
  d=$(dirname "$f")
  [ -f "$d/exit_code" ] && continue
  [ -f "$d/pid" ] && kill -0 "$(cat "$d/pid")" 2>/dev/null && s=$((s + $(cat "$f")))
done
echo $s
EOF
)
if [ $((used + threads)) -gt "$MAX_THREADS" ] && [ "${FORCE:-0}" != 1 ]; then
  echo "thread budget: $used in use + $threads requested > $MAX_THREADS (FORCE=1 to override)" >&2
  exit 1
fi

run_rel="$phase/$(date +%Y%m%d-%H%M)_$name"
run_dir="$HPC_ROOT/runs/$run_rel"
session="bv_$name"
if ssh -o BatchMode=yes "$HPC" "tmux has-session -t '$session' 2>/dev/null"; then
  echo "tmux session $session is still running; pick another name" >&2
  exit 1
fi

# $cmd is pasted literally into run.sh and evaluated on the HPC.
run_sh=$(cat <<EOF
#!/usr/bin/env bash
cd $HPC_ROOT/src
source $HPC_VENV/bin/activate
export PYTHONPATH=$HPC_ROOT/src RUN_DIR=$run_dir
export OMP_NUM_THREADS=$threads MKL_NUM_THREADS=$threads OPENBLAS_NUM_THREADS=$threads NUMBA_NUM_THREADS=$threads
echo \$\$ > $run_dir/pid
nice -n $NICE $cmd > $run_dir/log.txt 2>&1
echo \$? > $run_dir/exit_code
EOF
)
ssh -o BatchMode=yes "$HPC" "mkdir -p '$run_dir' && cat > '$run_dir/run.sh' && chmod +x '$run_dir/run.sh'" <<<"$run_sh"
ssh -o BatchMode=yes "$HPC" "cat > '$run_dir/cmd.txt'" <<<"$cmd"
ssh -o BatchMode=yes "$HPC" "echo $local_head > '$run_dir/git_commit.txt' && echo $threads > '$run_dir/threads' \
  && tmux new-session -d -s '$session' 'bash $run_dir/run.sh'"
echo "submitted: runs/$run_rel  (tmux session $session, $threads threads)"
