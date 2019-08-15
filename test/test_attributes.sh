#!/usr/bin/env bash
set -e

[ -z "${BETEXC_PYTHON}" ] && export BETEXC_PYTHON=python

function test_str {
    echo -e "\n${1}\n"

    # first, test with regular args
    "${BETEXC_PYTHON}" "${@}" || true

    echo ''

    # now test with a condensed argument
    cmd="${1}"
    shift

    "${BETEXC_PYTHON}" "$cmd" "${@}" || true
}

test_str test/test_util/test_attributes.py

