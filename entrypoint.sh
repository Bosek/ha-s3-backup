#!/usr/bin/env sh

set -e

echo "Creating crontab"
printf "${CRON_SCHEDULE} /usr/local/bin/python3 /home/app/main.py > /proc/1/fd/1 2>/proc/1/fd/2\n" > /tmp/crontab
crontab - < /tmp/crontab

echo "Starting $@"
exec "$@"