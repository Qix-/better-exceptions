# -*- coding:utf-8 -*-

import better_exceptions
better_exceptions.hook()


def add(a, b, c):
    return (a + b + \
            c)

def test(string):
    add(1
        , string, 3)

test("""multi-lines
""")
