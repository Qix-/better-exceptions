# -*- coding:utf-8 -*-

import better_exceptions
better_exceptions.hook()
better_exceptions.MAX_LENGTH = 10

def div():
    var = "9" * 150
    return 1 / var


div()
