#!/usr/bin/env bash
set -euo pipefail

usage() {
	echo "Usage: open_local_url.sh <url>" >&2
}

if [ "$#" -ne 1 ]; then
	usage
	exit 2
fi

url=$1

if command -v open >/dev/null 2>&1; then
	open "$url"
elif command -v xdg-open >/dev/null 2>&1; then
	xdg-open "$url" >/dev/null 2>&1 || true
else
	echo "Open this URL in your browser: $url"
fi
