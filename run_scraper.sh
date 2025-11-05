#!/bin/zsh
export PATH=/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin
cd /Users/iroiropro/dev/carsenser-scraper
echo "$(date) cron reached script" >> /tmp/cron_debug.log
# pyenvはcron環境では動かないためvenvのPythonを直接使う
source /Users/iroiropro/dev/carsenser-scraper/.venv/bin/activate
/Users/iroiropro/dev/carsenser-scraper/.venv/bin/python /Users/iroiropro/dev/carsenser-scraper/scraper.py >> /tmp/carsenser_test.log 2>&1
