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

## See Also

- [paradoxxxzero/better-exceptions-hook](https://github.com/paradoxxxzero/better-exceptions-hook) - removes the need to `import better_exceptions` by adding a startup hook

# License
Copyright &copy; 2017, Josh Junon. Licensed under the [MIT license](LICENSE.txt).
