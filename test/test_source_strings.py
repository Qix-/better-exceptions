# -*- coding:utf-8 -*-

import better_exceptions
better_exceptions.hook()


a = b = 0
a + b"prefix" + 'single' + """triple""" + 1 + b
