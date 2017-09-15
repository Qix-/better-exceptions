#!/usr/bin/env bash
set -e

[ -z "${BETEXC_PYTHON}" ] && export BETEXC_PYTHON=python

function test_str {
	echo -e "\n${1}\n"

	# first, test with regular args
	"${BETEXC_PYTHON}" -c "${@}" || true

	echo ''

	# now test with a condensed argument
	cmd="${1}"
	shift
	"${BETEXC_PYTHON}" -c"$cmd" "${@}" || true
}

test_str 'import better_exceptions; better_exceptions.hook(); a = 5; assert a > 10 # this should work fine' these extra arguments should be removed and should not show up 'in' the output
test_str 'from __future__ import print_function; import better_exceptions; better_exceptions.hook(); a = "why hello there"; print(a); assert False'
test_str 'from __future__ import print_function; import better_exceptions; better_exceptions.hook(); a = "why     hello          " + "   there"; print(a); assert False'
