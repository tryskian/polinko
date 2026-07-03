#!/usr/bin/env sh

_polinko_shell_command_common=${SHELL_COMMAND_COMMON_SCRIPT:-${script_dir:-./tools}/shell_command_common.sh}
# shellcheck source=./tools/shell_command_common.sh
. "$_polinko_shell_command_common"

polinko_pid_is_positive_integer() {
	_polinko_pid_value=$1
	case "$_polinko_pid_value" in
	"" | *[!0123456789]*)
		return 1
		;;
	esac
	case "$_polinko_pid_value" in
	*[!0]*)
		return 0
		;;
	esac
	return 1
}

polinko_pid_is_running() {
	_polinko_pid=$1
	polinko_pid_is_positive_integer "$_polinko_pid" || return 1
	kill -0 "$_polinko_pid" 2>/dev/null || return 1
	_polinko_pid_state=$(
		ps -o stat= -p "$_polinko_pid" 2>/dev/null | tr -d ' ' || true
	)
	case "$_polinko_pid_state" in
		Z*)
			return 1
			;;
	esac
	return 0
}

polinko_require_process_inspection() {
	_polinko_context=${1:-process lifecycle PID inspection}
	polinko_require_command ps "$_polinko_context"
}

polinko_invalid_numeric_value() {
	_polinko_name=$1
	_polinko_value=$2
	_polinko_expected=$3
	_polinko_context=${4:-runtime helper}
	echo "Invalid numeric value for $_polinko_context: $_polinko_name must be $_polinko_expected (got $_polinko_value)" >&2
	return 1
}

polinko_require_non_empty_token() {
	_polinko_name=$1
	_polinko_value=$2
	_polinko_kind=${3:-value}
	_polinko_context=${4:-runtime helper}
	case "$_polinko_value" in
	"" | *[[:space:]]*)
		echo "Invalid value for $_polinko_context: $_polinko_name must be a non-empty $_polinko_kind without whitespace (got $_polinko_value)" >&2
		return 1
		;;
	esac
	return 0
}

polinko_require_positive_integer() {
	_polinko_name=$1
	_polinko_value=$2
	_polinko_context=${3:-runtime helper}
	case "$_polinko_value" in
	"" | *[!0123456789]*)
		polinko_invalid_numeric_value "$_polinko_name" "$_polinko_value" "a positive integer" "$_polinko_context"
		return $?
		;;
	esac
	case "$_polinko_value" in
	*[!0]*)
		return 0
		;;
	esac
	polinko_invalid_numeric_value "$_polinko_name" "$_polinko_value" "a positive integer" "$_polinko_context"
}

polinko_require_non_negative_integer() {
	_polinko_name=$1
	_polinko_value=$2
	_polinko_context=${3:-runtime helper}
	case "$_polinko_value" in
	"" | *[!0123456789]*)
		polinko_invalid_numeric_value "$_polinko_name" "$_polinko_value" "a non-negative integer" "$_polinko_context"
		return $?
		;;
	esac
	return 0
}

polinko_require_non_negative_decimal() {
	_polinko_name=$1
	_polinko_value=$2
	_polinko_context=${3:-runtime helper}
	case "$_polinko_value" in
	"" | *[!0123456789.]* | .* | *.*.* | *.)
		polinko_invalid_numeric_value "$_polinko_name" "$_polinko_value" "a non-negative decimal number" "$_polinko_context"
		return $?
		;;
	esac
	return 0
}

polinko_require_tcp_port() {
	_polinko_name=$1
	_polinko_value=$2
	_polinko_context=${3:-runtime helper}
	if ! polinko_require_positive_integer \
		"$_polinko_name" \
		"$_polinko_value" \
		"$_polinko_context"; then
		return 1
	fi
	if [ "${#_polinko_value}" -gt 5 ] || [ "$_polinko_value" -gt 65535 ]; then
		polinko_invalid_numeric_value \
			"$_polinko_name" \
			"$_polinko_value" \
			"a TCP port from 1 to 65535" \
			"$_polinko_context"
		return $?
	fi
	return 0
}

polinko_url_explicit_port() {
	_polinko_url=$1
	case "$_polinko_url" in
	*://*)
		;;
	*)
		return 1
		;;
	esac
	_polinko_authority=${_polinko_url#*://}
	_polinko_authority=${_polinko_authority%%/*}
	_polinko_authority=${_polinko_authority%%\?*}
	_polinko_authority=${_polinko_authority%%\#*}
	case "$_polinko_authority" in
	*:*)
		_polinko_port=${_polinko_authority##*:}
		;;
	*)
		return 1
		;;
	esac
	case "$_polinko_port" in
	"" | *[!0123456789]*)
		return 2
		;;
	esac
	printf "%s\n" "$_polinko_port"
}

polinko_require_url_port_matches() {
	_polinko_name=$1
	_polinko_url=$2
	_polinko_port=$3
	_polinko_context=${4:-runtime helper}
	_polinko_status=0
	_polinko_url_port=$(polinko_url_explicit_port "$_polinko_url" 2>/dev/null) ||
		_polinko_status=$?
	if [ "$_polinko_status" -eq 1 ]; then
		echo "Invalid URL value for $_polinko_context: $_polinko_name must include an explicit port matching $_polinko_port (got $_polinko_url)" >&2
		return 1
	elif [ "$_polinko_status" -ne 0 ]; then
		echo "Invalid URL value for $_polinko_context: $_polinko_name is not a valid URL with an explicit port (got $_polinko_url)" >&2
		return 1
	fi
	if [ "$_polinko_url_port" != "$_polinko_port" ]; then
		echo "Invalid URL value for $_polinko_context: $_polinko_name port must match $_polinko_port (got $_polinko_url)" >&2
		return 1
	fi
}

polinko_join_path() {
	_polinko_path_root=$1
	_polinko_path_leaf=${2#/}
	case "$_polinko_path_root" in
	"")
		printf "%s\n" "$_polinko_path_leaf"
		;;
	/)
		printf "/%s\n" "$_polinko_path_leaf"
		;;
	*/)
		printf "%s%s\n" "$_polinko_path_root" "$_polinko_path_leaf"
		;;
	*)
		printf "%s/%s\n" "$_polinko_path_root" "$_polinko_path_leaf"
		;;
	esac
}

polinko_wait_for_pid_exit() {
	_polinko_pid=$1
	_polinko_attempts=${2:-50}
	_polinko_sleep_seconds=${3:-0.1}
	_polinko_attempt=0
	while polinko_pid_is_running "$_polinko_pid"; do
		if [ "$_polinko_attempt" -ge "$_polinko_attempts" ]; then
			return 1
		fi
		sleep "$_polinko_sleep_seconds"
		_polinko_attempt=$((_polinko_attempt + 1))
	done
	return 0
}

polinko_process_command() {
	_polinko_pid=$1
	ps -o command= -p "$_polinko_pid" 2>/dev/null || true
}

polinko_parent_pid() {
	_polinko_pid=$1
	ps -o ppid= -p "$_polinko_pid" 2>/dev/null | tr -d ' ' || true
}

if [ "${0##*/}" = "process_lifecycle_common.sh" ]; then
	echo "Source this helper from runtime shell scripts instead of executing it directly." >&2
	exit 2
fi
