# -*- coding:utf-8 -*-

import better_exceptions
better_exceptions.hook()

code = """
if True:
    a = 5
        print("foobar")  #intentional faulty indentation here.
    b = 7
"""

exec(code)
