# -*- coding:utf-8 -*-

import byomkesh_bakshi
byomkesh_bakshi.hook()
byomkesh_bakshi.MAX_LENGTH = None

def div():
    var = "9" * 150
    return 1 / var


div()
