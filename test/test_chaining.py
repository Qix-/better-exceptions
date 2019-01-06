# -*- coding:utf-8 -*-

import better_exceptions
better_exceptions.hook()

def div(x, y):
    x / y

def cause(x, y):
    try:
        div(x, y)
    except Exception:
        raise ValueError("Division error")

def context(x, y):
    try:
        cause(x, y)
    except Exception as e:
        raise ValueError("Cause error") from e

context(1, 0)
