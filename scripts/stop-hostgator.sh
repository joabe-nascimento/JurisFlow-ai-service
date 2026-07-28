#!/bin/bash
# Para o JurisFlow AI no HostGator.
set -eu

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib-hostgator.sh
source "$SCRIPT_DIR/lib-hostgator.sh"

jurisflow_stop
echo "JurisFlow parado (porta $PORT)."
