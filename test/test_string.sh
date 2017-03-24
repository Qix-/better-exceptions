#!/usr/bin/env bash
set -e

[ -z "${BETEXC_PYTHON}" ] && export BETEXC_PYTHON=python

TEST_STR='import better_exceptions; a = 5; assert a > 10 # this should work fine'

"${BETEXC_PYTHON}" -c "${TEST_STR}" these extra arguments should be removed and should not show up 'in' the output
