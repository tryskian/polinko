#!/usr/bin/env bash
set -euo pipefail

usage() {
	echo "Usage: open_local_url.sh <url>" >&2
}

is_local_url() {
	[[ "$1" =~ ^https?://localhost(:[0-9]+)?(/.*)?$ ]] ||
		[[ "$1" =~ ^https?://127(\.[0-9]{1,3}){3}(:[0-9]+)?(/.*)?$ ]] ||
		[[ "$1" =~ ^https?://\[::1\](:[0-9]+)?(/.*)?$ ]]
}

if [ "$#" -ne 1 ]; then
	usage
	exit 2
fi

url=$1

if ! is_local_url "$url"; then
	echo "Refusing to launch non-local URL: $url" >&2
	exit 2
fi

if command -v open >/dev/null 2>&1; then
	open "$url"
elif command -v xdg-open >/dev/null 2>&1; then
	xdg-open "$url" >/dev/null 2>&1 || true
else
	echo "Open this URL in your browser: $url"
fi
