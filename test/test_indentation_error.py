# -*- coding:utf-8 -*-

import byomkesh_bakshi
byomkesh_bakshi.hook()

code = """
if True:
    a = 5
        print("foobar")  #intentional faulty indentation here.
    b = 7
"""

exec(code)
