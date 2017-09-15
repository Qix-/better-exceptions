import better_exceptions
better_exceptions.hook()

foo = 52


def shallow(a, b):
    deep(a + b)


def deep(val):
    global foo
    assert val > 10 and foo == 60


bar = foo - 50
shallow(bar, 15)
shallow(bar, 2)
