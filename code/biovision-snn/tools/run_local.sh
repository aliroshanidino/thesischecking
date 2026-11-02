#!/usr/bin/env bash
# Start a detached job on the laptop (DECISIONS D15). It survives the end of the Claude turn and keeps the
# machine awake while it runs (lid closed / manual sleep still sleep).
# Usage: tools/run_local.sh <name> <cmd...>     e.g. tools/run_local.sh s1_stdp python -m biovision.experiments.phase0 ...
# Creates work/runs/<phase>/<YYYYmmdd-HHMM>_<name>/ with cmd.txt, git_commit.txt, device.json, log.txt,
# exit_code (when finished) and .running (while running). `python` in <cmd> is the repo's .venv.
set -euo pipefail
source "$(dirname "$0")/local.env"
[ $# -ge 2 ] || { echo "usage: $0 <name> <cmd...>" >&2; exit 2; }
name=$1; shift; cmd="$*"
[[ "$name" =~ ^[A-Za-z0-9_.-]+$ ]] || { echo "name must match [A-Za-z0-9_.-]+" >&2; exit 2; }
cd "$REPO"
branch=$(git rev-parse --abbrev-ref HEAD)
case "$branch" in phase-*) phase="phase${branch#phase-}" ;; *) phase="$branch" ;; esac
if [ -n "$(find "$WORK/runs" -name .running 2>/dev/null)" ] && [ "${FORCE:-0}" != 1 ]; then
  echo "another job is running (one GPU job at a time; FORCE=1 to override):" >&2
  find "$WORK/runs" -name .running -printf '  %h\n' >&2; exit 1
fi
bash "$REPO/tools/local_health.sh" > /dev/null || { echo "local_health.sh reports a problem; run it and ask the user" >&2; exit 1; }
run_dir="$WORK/runs/$phase/$(date +%Y%m%d-%H%M)_$name"
mkdir -p "$run_dir"
git rev-parse HEAD > "$run_dir/git_commit.txt"
if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
  echo "warning: uncommitted changes are part of this run (saved to git_dirty.diff)" >&2
  git diff > "$run_dir/git_dirty.diff"
fi
printf '%s\n' "$cmd" > "$run_dir/cmd.txt"
win() { cygpath -m "$1"; }
cat > "$run_dir/run.sh" <<EOF
#!/usr/bin/env bash
cd "$REPO"
export PATH="$REPO/.venv/Scripts:\$PATH" PYTHONPATH="$REPO" RUN_DIR="$run_dir" PYTHONUNBUFFERED=1
touch "$run_dir/.running"
powershell -NoProfile -ExecutionPolicy Bypass -File "$(win "$REPO/tools/keep_awake.ps1")" -Flag "$(win "$run_dir/.running")" &
echo \$\$ > "$run_dir/pid"
python -c "import json; from biovision.engine.device import describe, resolve_device; print(json.dumps(describe(resolve_device('auto')), indent=1))" > "$run_dir/device.json" 2>&1
{ $cmd
} > "$run_dir/log.txt" 2>&1
echo \$? > "$run_dir/exit_code"
rm -f "$run_dir/.running"
EOF
bash_exe=$(cygpath -w "$(command -v bash)")
powershell -NoProfile -Command "Start-Process -WindowStyle Hidden -FilePath '$bash_exe' -ArgumentList '-l','\"$(win "$run_dir/run.sh")\"'"
echo "started: ${run_dir#$WORK/}"
