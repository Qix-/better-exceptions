# -*- coding:utf-8 -*-

import better_exceptions
better_exceptions.hook()


def _deep(val):
    return 1 / val

def div():
    return _deep("天")


div()
