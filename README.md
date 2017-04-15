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

### IPython

If you are using IPython, you will need to register a startup hook for better_exceptions.

Add this code to `$HOME/.ipython/profile_default/startup/00-better_exceptions.py`:

```python
from __future__ import print_function
import better_exceptions, sys

ip = get_ipython()
old_show = ip.showtraceback

def exception_thunk(exc_tuple=None, filename=None,
                    tb_offset=None, exception_only=False):
    print("Thunk: %r %r %r %r" % (exc_tuple, filename, tb_offset, exception_only),
          file=sys.stderr)
    notuple = False
    if exc_tuple is None:
        notuple = True
        exc_tuple = sys.exc_info()
    use_better = True
    use_better = use_better and (filename is None)
    use_better = use_better and (tb_offset is None)
    use_better = use_better and (not exception_only)
    use_better = use_better and (not isinstance(exc_tuple[0], SyntaxError))
    if use_better:
        return better_exceptions.excepthook(*exc_tuple)
    else:
        return old_show(None if notuple else exc_tuple,
                        filename, tb_offset, exception_only)

ip.showtraceback = exception_thunk
```

### Advanced Usage

If you want to allow the entirety of values to be outputted instead of being truncated to a certain amount of characters:

```python
better_exceptions.MAX_LENGTH = None
```

## See Also

- [paradoxxxzero/better-exceptions-hook](https://github.com/paradoxxxzero/better-exceptions-hook) - removes the need to `import better_exceptions` by adding a startup hook

# License
Copyright &copy; 2017, Josh Junon. Licensed under the [MIT license](LICENSE.txt).
