#!/usr/bin/env bash
# Lightweight detached watcher: logs GEARS Replogle RL1 progress every 10 min.
set -u
LOGDIR="logs"
WLOG="$LOGDIR/rl1_watch.log"
while true; do
  D=$(ls -td results/replogle/gears/rl1_k562_* 2>/dev/null | head -1)
  P=""
  if [ -n "$D" ] && [ -f "$D/raw_train_telemetry.log" ]; then
    P=$(grep -a "Step" "$D/raw_train_telemetry.log" | tail -1)
  fi
  M=$(ps aux | grep run_gears_replogle_rl1 | grep -v grep | awk '{print $3"%cpu", $4"%mem"}' | head -1)
  E=$(ls -td "$D" 2>/dev/null | xargs -I{} sh -c 'grep -a "Overall MSE" "{}"/raw_train_telemetry.log 2>/dev/null | tail -1')
  printf "%s | mem[%s] | %s | %s\n" "$(date +%H:%M:%S)" "$M" "$P" "$E" >> "$WLOG"
  sleep 600
done