#!/usr/bin/env bash

set -e

if [[ "${1}" == "generate" ]]; then
	rm -rf test/output
	mkdir -p test/output
	GENERATE=true
else
	GENERATE=false
fi

cd "$(dirname "${0}")"
PYTHONPATH="$(pwd):$(pwd)/test"
export PYTHONPATH

function normalize {
	# we translate anything that looks like an address into 0xDEADBEEF
	# since the addresses change from run to run and break diff testing
	cat | sed 's|0x[a-fA-F0-9]\{1,\}|0xDEADBEEF|g' | sed 's|<module '"'[^']*' from '[^']*'>|<module 'test_module' from '/removed/for/test/purposes.py'>"'|g' | sed 's|File "/[^"]*"|File "/removed/for/test/purposes.ext"|g' | grep -v "bash: warning:"
}

function test_case {
	echo -e "\x1b[36;1m   " "$@" "\x1b[m" 1>&2

	echo "$@"
	echo -e "\n"
	("$@" 2>&1 || true) | normalize
	echo -e "\n\n"

	return $?
}

function test_all {
	test_case "$BETEXC_PYTHON" "test/test.py"
	test_case "$BETEXC_PYTHON" "test/test_color.py"
	test_case "$BETEXC_PYTHON" "test/test_encoding.py"
	test_case "./test/test_interactive.sh"
	# test_case "./test/test_interactive_raw.sh"
	test_case "./test/test_string.sh"
	test_case "$BETEXC_PYTHON" "test/test_logging.py"
	test_case "$BETEXC_PYTHON" "test/test_truncating.py"
	test_case "$BETEXC_PYTHON" "test/test_truncating_disabled.py"
	test_case "$BETEXC_PYTHON" "test/test_indentation_error.py"
	test_case "$BETEXC_PYTHON" "test/test_syntax_error.py"
	test_case "$BETEXC_PYTHON" "test/test_unittest_patch.py"

	if [[ "$BETEXC_PYTHON" == "python3" ]]; then
		test_case "$BETEXC_PYTHON" "test/test_chaining.py"
	fi
}

for encoding in ascii "UTF-8"; do
	for term in xterm vt100 dumb; do
		for color in 0 1; do
			for pv in 2 3; do
				[[ $color == "1" ]] && color_filename="color" || color_filename="nocolor"
				filename="test/output/python${pv}-${term}-${encoding}-${color_filename}.out"

				export LANG="en_US.${encoding}"
				export LC_ALL="${LANG}"
				export PYTHONCOERCECLOCALE=0
				export PYTHONUTF8=0
				export TERM="${term}"
				export FORCE_COLOR="${color}"
				export BETEXC_PYTHON="python${pv}"

				echo -e "\x1b[35;1m${filename}\x1b[m" >&2
				if $GENERATE; then
					exec > "$filename"
					test_all "$filename"
				else
					test_all | diff "$(pwd)/${filename}" -
				fi
			done
		done
	done
done
