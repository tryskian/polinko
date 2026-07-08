#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/repo_root.sh
source "$script_dir/repo_root.sh"
# shellcheck source=tools/shell_command_common.sh
source "$script_dir/shell_command_common.sh"

polinko_cd_repo_root

GH_BIN="gh"
BASE="main"
HEAD=""
TITLE=""
BODY_FILE=""

usage() {
	cat <<'USAGE'
Usage:
  tools/github_pr_create.sh --head <branch> --title <title> --body-file <path|->

Options:
  --gh <command>        GitHub CLI executable. Defaults to gh.
  --base <branch>       Base branch. Defaults to main.
  --head <branch>       Head branch for the pull request.
  --title <title>       Pull request title.
  --body-file <path|->  Markdown body file, or - to read from quoted stdin.

PR bodies must be passed as a file or stdin through gh --body-file. Do not pass
Markdown, code spans, or backticks through an inline gh pr create --body string.
USAGE
}

fail() {
	echo "github-pr-create: FAIL" >&2
	echo "  $1" >&2
	echo "  use --body-file <path|-> for PR Markdown; use - only with quoted stdin" >&2
	exit 2
}

while (($#)); do
	case "$1" in
		--gh)
			[[ $# -ge 2 ]] || fail "--gh requires a value"
			GH_BIN="$2"
			shift 2
			;;
		--base)
			[[ $# -ge 2 ]] || fail "--base requires a value"
			BASE="$2"
			shift 2
			;;
		--head)
			[[ $# -ge 2 ]] || fail "--head requires a value"
			HEAD="$2"
			shift 2
			;;
		--title)
			[[ $# -ge 2 ]] || fail "--title requires a value"
			TITLE="$2"
			shift 2
			;;
		--body-file)
			[[ $# -ge 2 ]] || fail "--body-file requires a value"
			BODY_FILE="$2"
			shift 2
			;;
		--help|-h)
			usage
			exit 0
			;;
		*)
			fail "unknown argument: $1"
			;;
	esac
done

[[ -n "$BASE" ]] || fail "--base must not be empty"
[[ -n "$HEAD" ]] || fail "--head is required"
[[ -n "$TITLE" ]] || fail "--title is required"
[[ -n "$BODY_FILE" ]] || fail "--body-file is required"

if ! polinko_command_available "$GH_BIN"; then
	fail "GitHub CLI executable is not available: $GH_BIN"
fi

if [[ "$BODY_FILE" != "-" && ! -r "$BODY_FILE" ]]; then
	fail "body file is not readable: $BODY_FILE"
fi

if [[ "$BODY_FILE" == "-" && -t 0 ]]; then
	fail "--body-file - requires piped stdin or a quoted heredoc"
fi

exec "$GH_BIN" pr create \
	--base "$BASE" \
	--head "$HEAD" \
	--title "$TITLE" \
	--body-file "$BODY_FILE"
