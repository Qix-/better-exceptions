import better_exceptions

foo = 52


def shallow(a, b):
    """The first function that is called"""
    deep(a + b)


def deep(val):
    """The second (last) function that is called
    in the test case.

    This is where exceptions come from."""
    global foo
    assert val > 10 and foo == 60


bar = foo - 50
shallow(bar, 15)
shallow(bar, 2)
