import builtins
import io
import keyword
import tokenize


STYLE = {
    'builtin': '\x1b[35;1m{}\x1b[m',
    'comment': '\x1b[2;37m{}\x1b[m',
    'constant': '{}',
    'identifier': '{}',
    'keyword': '\x1b[33;1m{}\x1b[m',
    'number': '\x1b[31m{}\x1b[m',
    'operator': '{}',
    'other': '{}',
    'punctuation': '{}',
    'string': '\x1b[31m{}\x1b[m',
}


class Highlighter(object):

    def __init__(self, style):
        self._style = style
        self._builtins = dir(builtins)
        self._punctation = {'(', ')', '[', ']', '{', '}', ':', ',', ';'}
        self._constants = {'True', 'False', 'None'}

    def highlight(self, source):
        style = self._style
        row, column = 0, 0
        output = ""

        for token in self.tokenize(source):
            type_, string, start, end, line = token

            if type_ == tokenize.NAME:
                if string in self._constants:
                    color = style['constant']
                elif keyword.iskeyword(string):
                    color = style['keyword']
                elif string in self._builtins:
                    color = style['builtin']
                else:
                    color = style['identifier']
            elif type_ == tokenize.OP:
                if string in self._punctation:
                    color = style['punctuation']
                else:
                    color = style['operator']
            elif type_ == tokenize.NUMBER:
                color = style['number']
            elif type_ == tokenize.STRING:
                color = style['string']
            elif type_ == tokenize.COMMENT:
                color = style['comment']
            else:
                color = style['other']

            start_row, start_column = start
            _, end_column = end

            if start_row != row:
                source = source[:column]
                row, column = start_row, 0

            if type_ != tokenize.ENCODING:
                output += line[column:start_column]
                output += color.format(string)

            column = end_column

        output += source[column:]

        return output

    @staticmethod
    def tokenize(source):
        source = source.encode("utf-8")
        source = io.BytesIO(source)

        try:
            yield from tokenize.tokenize(source.readline)
        except tokenize.TokenError:
            return
