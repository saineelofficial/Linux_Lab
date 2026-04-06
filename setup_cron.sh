#!/bin/bash

# setup_cron.sh
# This script configures a cron job to run the Python monitor every 5 minutes.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONITOR_SCRIPT="$SCRIPT_DIR/monitor.py"

if [ ! -f "$MONITOR_SCRIPT" ]; then
    echo "Error: $MONITOR_SCRIPT not found."
    exit 1
fi

# Make the python script executable (if not already)
chmod +x "$MONITOR_SCRIPT"

CRON_JOB="*/5 * * * * /usr/bin/env python3 $MONITOR_SCRIPT >> $SCRIPT_DIR/logs/cron.log 2>&1"

# Check if the job already exists
(crontab -l 2>/dev/null | grep -F "$MONITOR_SCRIPT") > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "The cron job is already installed."
    exit 0
fi

# Add the job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
if [ $? -eq 0 ]; then
    echo "Successfully installed cron job to run every 5 minutes."
    echo "Cron job: $CRON_JOB"
else
    echo "Failed to install cron job."
    exit 1
fi
