from sys import exc_info
from better_exceptions import excepthook

def skip_errors_filter(record):
    return not record.exc_info

class BetterExceptionsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, _, exception):
        _, _, traceback = exc_info()
        excepthook(exception.__class__, exception, traceback)
