import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import better_exceptions
better_exceptions.hook()

class C():
    pass

testc = C()
testc.v = 2
testc.cc = C()
testc.cc.e = 'e'

testc.v * len(testc.cc.e) / 0
