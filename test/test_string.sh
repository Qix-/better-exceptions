#!/usr/bin/env bash
set -e

TEST_STR='import better_exceptions; a = 5; assert a > 10'

"${BETEXC_PYTHON}" -c "${TEST_STR}"
