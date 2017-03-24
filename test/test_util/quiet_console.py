import code

class QuietConsole(code.InteractiveConsole, object):
    def __init__(self):
        super(self.__class__, self).__init__()

    def interact(self):
        return super(self.__class__, self).interact('')


if __name__ == '__main__':
    QuietConsole().interact()
