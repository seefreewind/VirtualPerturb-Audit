#!/usr/bin/env bash
# Waits for the K562 RL1 full run to complete, then launches RPE1 RL1 full run.
# Logs to logs/rl1_sequencer.log
set -u
WLOG="logs/rl1_sequencer.log"
echo "$(date +%H:%M:%S) sequencer started" >> "$WLOG"
while true; do
  D=$(ls -td results/replogle/gears/rl1_k562_* 2>/dev/null | head -1)
  if [ -n "$D" ] && [ -f "$D/metadata.json" ]; then
    S=$(python3 -c "import json,sys; print(json.load(open('$D/metadata.json')).get('run_status',''))" 2>/dev/null)
    if [ "$S" = "COMPLETED_GEARS" ]; then
      echo "$(date +%H:%M:%S) K562 COMPLETED ($D); launching RPE1" >> "$WLOG"
      nohup env PYTHONPATH=. environment/gears-venv/bin/python scripts/run_gears_replogle_rl1.py --dataset rpe1 > logs/rl1_rpe1.log 2>&1 &
      echo "$(date +%H:%M:%S) RPE1 launched pid $!" >> "$WLOG"
      exit 0
    fi
    if [ "$S" = "FAILED_GEARS" ] || [ "$S" = "FAILED" ]; then
      echo "$(date +%H:%M:%S) K562 FAILED; NOT launching RPE1 (needs intervention)" >> "$WLOG"
      exit 2
    fi
  fi
  sleep 240
done