# -*- coding:utf-8 -*-

import byomkesh_bakshi
byomkesh_bakshi.hook()


def _deep(val):
    return 1 / val

def div():
    return _deep("天")


div()
