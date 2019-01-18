# -*- coding:utf-8 -*-

import better_exceptions
better_exceptions.hook()


class A:

    def __repr__(self):
        return ("[[1, 2, 3]\n"
                " [4, 5, 6]\n"
                " [7, 8, 9]]")

def multiline():
    a = b = A()
    a + b

multiline()
