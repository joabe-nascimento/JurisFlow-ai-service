#!/bin/bash
# Wrapper legado — o cron deve usar scripts/watchdog-hostgator.sh diretamente.
exec "$(dirname "$0")/scripts/watchdog-hostgator.sh"
