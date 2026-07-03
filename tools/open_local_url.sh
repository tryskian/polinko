#!/usr/bin/env bash
set -euo pipefail

usage() {
	echo "Usage: open_local_url.sh <url>" >&2
}

is_loopback_ipv4_host() {
	local host=$1
	local octet

	[[ "$host" =~ ^127\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})$ ]] ||
		return 1

	for octet in "${BASH_REMATCH[@]:1}"; do
		((10#$octet <= 255)) || return 1
	done
}

is_local_url() {
	local url=$1
	local host

	[[ "$url" =~ ^https?://localhost(:[0-9]+)?([/\?\#].*)?$ ]] && return 0
	[[ "$url" =~ ^https?://\[::1\](:[0-9]+)?([/\?\#].*)?$ ]] && return 0

	if [[ "$url" =~ ^https?://([^/:]+)(:[0-9]+)?([/\?\#].*)?$ ]]; then
		host=${BASH_REMATCH[1]}
		is_loopback_ipv4_host "$host"
		return
	fi

	return 1
}

if [ "$#" -ne 1 ]; then
	usage
	exit 2
fi

script_path=${BASH_SOURCE[0]}
script_dir=${script_path%/*}
if [ "$script_dir" = "$script_path" ]; then
	script_dir=.
fi
# shellcheck source=tools/shell_command_common.sh
source "$script_dir/shell_command_common.sh"

url=$1

if ! is_local_url "$url"; then
	echo "Refusing to launch non-local URL: $url" >&2
	exit 2
fi

if polinko_command_available open; then
	if ! open "$url"; then
		echo "Failed to launch local URL with open: $url" >&2
		exit 1
	fi
elif polinko_command_available xdg-open; then
	if ! xdg-open "$url" >/dev/null 2>&1; then
		echo "Failed to launch local URL with xdg-open: $url" >&2
		exit 1
	fi
else
	echo "Open this URL in your browser: $url"
fi
