import io
import sys
import unittest
import better_exceptions

STREAM = io.BytesIO() if sys.version_info[0] == 2 else io.StringIO()


def add(a, b):
    return a + b


class MyTestCase(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(1, "2"), 3)


class SilentTestRunner(unittest.TextTestRunner):
    """
    The default TextTestRunner will print something like 'Ran 1 test in 0.017s'
    into stderr, and values are different from different tests. To ensure that
    CI script can compare between the outputs, those information must be muted.
    """

    def __init__(self, stream=STREAM, *args, **kwargs):
        super(SilentTestRunner, self).__init__(STREAM, *args, **kwargs)


def print_test_error():
    test = unittest.main(exit=False, testRunner=SilentTestRunner)
    error = test.result.errors[0][1]
    # unittest.TestResult.errors is "A list containing 2-tuples of TestCase
    # instances and strings holding formatted tracebacks. Each tuple represents
    # a test which raised an unexpected exception."
    assert isinstance(error, str)
    lines = error.splitlines()
    print("\n".join(lines[4:]))  # remove '/removed/for/test/purposes.py'


def main():
    print_test_error()

    def patch(self, err, test):
        lines = better_exceptions.format_exception(*err)
        if sys.version_info[0] == 2:
            return u"".join(lines).encode("utf-8")
        else:
            return u"".join(lines)

    unittest.result.TestResult._exc_info_to_string = patch

    print_test_error()


if __name__ == "__main__":
    main()
