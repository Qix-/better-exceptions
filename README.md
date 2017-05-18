# better-exceptions [![Travis](https://img.shields.io/travis/Qix-/better-exceptions.svg?style=flat-square)](https://travis-ci.org/Qix-/better-exceptions)

Pretty and more helpful exceptions in Python, automatically.

![Example screenshot of exceptions](screenshot.png)

## Usage

Install `better_exceptions` via pip:

```console
$ pip install better_exceptions
```

And import it somewhere:

```python
import better_exceptions
```

That's it!

### Advanced Usage

If you want to allow the entirety of values to be outputted instead of being truncated to a certain amount of characters:

```python
better_exceptions.MAX_LENGTH = None
```

#### Make the traceback file lines more accessible

Did you ever want to quickly open a Python module directly on the line where an exception happened?

You can let *better-exceptions* transform the file and line of a traceback frame so that you can
open it with your favorite editor conveniently from command line:

```python
# File and line will be printed as: 'File "spam.py +6", in eggs
better_exceptions.FILE_LINE_STYLE = 'vi'  # vi spam.py +6
better_exceptions.FILE_LINE_STYLE = 'emacs'  # emacs spam.py +6
# File and line will be printed as: 'File "spam.py:6", in eggs
better_exceptions.FILE_LINE_STYLE = 'colon'  # atom spam.py:6
```

A sample traceback could look like this:

```python
Traceback (most recent call last):
  File "testing.py +17", in <module>
    foo(2)
    └ <function foo at 0x7f7d6ce16e18>
  File "testing.py +6", in foo
    bar(x + x)
    │   │   └ 2
    │   └ 2
    └ <function bar at 0x7f7d6b47fbf8>
  File "testing.py +10", in bar
    foobar(y + 2)
    │      └ 4
    └ <function foobar at 0x7f7d6b47fc80>
  File "testing.py +14", in foobar
    assert z == 10
           └ 6
AssertionError: assert z == 10
```

Available file-line-styles are:
* vi (`<file> +<line>`)
* emacs (`<file> +<line>`)
* colon (`<file>:<line>`)

## See Also

- [paradoxxxzero/better-exceptions-hook](https://github.com/paradoxxxzero/better-exceptions-hook) - removes the need to `import better_exceptions` by adding a startup hook

# License
Copyright &copy; 2017, Josh Junon. Licensed under the [MIT license](LICENSE.txt).
