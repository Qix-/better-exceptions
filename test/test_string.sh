#!/usr/bin/env bash
set -e

[ -z "${BETEXC_PYTHON}" ] && export BETEXC_PYTHON=python

TEST_STR='import better_exceptions; a = 5; assert a > 10'

"${BETEXC_PYTHON}" -c "${TEST_STR}"
