#!/usr/bin/env bash
# Wait for both Replogle RL1 full runs, then build downstream tables/figures.
set -u

LOG="logs/rl1_postprocess.log"
mkdir -p logs
echo "$(date '+%Y-%m-%d %H:%M:%S') postprocess watcher started" >> "$LOG"

status_for() {
  local key="$1"
  local dir
  dir=$(ls -td "results/replogle/gears/rl1_${key}_"* 2>/dev/null | head -1)
  if [ -z "$dir" ] || [ ! -f "$dir/metadata.json" ]; then
    echo "MISSING"
    return 0
  fi
  python3 - "$dir/metadata.json" <<'PY'
import json, sys
try:
    meta = json.load(open(sys.argv[1]))
except Exception:
    print("UNREADABLE")
    raise SystemExit(0)
print(meta.get("run_status") or meta.get("status") or "UNKNOWN")
PY
}

dir_for() {
  local key="$1"
  ls -td "results/replogle/gears/rl1_${key}_"* 2>/dev/null | head -1
}

while true; do
  KS=$(status_for k562)
  RS=$(status_for rpe1)
  KD=$(dir_for k562)
  RD=$(dir_for rpe1)
  echo "$(date '+%Y-%m-%d %H:%M:%S') k562=${KS} ${KD} | rpe1=${RS} ${RD}" >> "$LOG"

  if [ "$KS" = "COMPLETED_GEARS" ] && [ "$RS" = "COMPLETED_GEARS" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') both runs complete; building RL1 analysis" >> "$LOG"
    if PYTHONPATH=. python3 scripts/build_gears_rl1_analysis.py >> "$LOG" 2>&1; then
      echo "$(date '+%Y-%m-%d %H:%M:%S') RL1 analysis complete; writing reports" >> "$LOG"
      PYTHONPATH=. python3 scripts/write_phase2a_rl1_reports.py >> "$LOG" 2>&1 || exit 2
      echo "$(date '+%Y-%m-%d %H:%M:%S') RL1 reports complete" >> "$LOG"
      exit 0
    else
      echo "$(date '+%Y-%m-%d %H:%M:%S') RL1 analysis failed; leaving watcher stopped for manual inspection" >> "$LOG"
      exit 2
    fi
  fi

  if [[ "$KS" == FAILED* ]] || [[ "$RS" == FAILED* ]]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') detected failed run; postprocess watcher exiting" >> "$LOG"
    exit 3
  fi

  sleep 600
done
