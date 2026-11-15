#!/usr/bin/env bash
set -euo pipefail

source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
bin_dir="$HOME/.local/bin"
pi_dir="${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}"
unit_dir="$HOME/.config/systemd/user"

mkdir -p "$bin_dir" "$pi_dir/extensions" "$unit_dir"
# Replace an older development symlink as well as a previous copied install.
[[ -L "$bin_dir/hc-agent-resume" ]] && rm "$bin_dir/hc-agent-resume"
install -m 755 "$source_dir/bin/hc-agent-resume" "$bin_dir/hc-agent-resume"
install -m 644 "$source_dir/integrations/pi/hc-agent-resume.ts" "$pi_dir/extensions/hc-agent-resume.ts"
install -m 644 "$source_dir/systemd/hc-agent-resumed.service" "$unit_dir/hc-agent-resumed.service"

systemctl --user daemon-reload
systemctl --user enable --now hc-agent-resumed.service
systemctl --user restart hc-agent-resumed.service

cat <<EOF
Installed hc-agent-resume and started hc-agent-resumed.service.
Reload Pi with /reload, then send a message in each Pi session you want to restore.
EOF
