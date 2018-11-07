# better-exceptions [![Travis](https://img.shields.io/travis/Qix-/better-exceptions.svg?style=flat-square)](https://travis-ci.org/Qix-/better-exceptions)

Pretty and more helpful exceptions in Python, automatically.

![Example screenshot of exceptions](screenshot.png)

## Usage

Install `byomkesh_bakshi` via pip:

```console
$ pip install byomkesh_bakshi
```

And set the `BYOMKESH_BAKSHI` environment variable to any value:

```bash
export BYOMKESH_BAKSHI=1  # Linux / OSX
setx BYOMKESH_BAKSHI 1    # Windows
```

That's it!

### Python REPL (Interactive Shell)

In order to use `byomkesh_bakshi` in the Python REPL, first install the package (as instructed above) and run:

```console
$ python -m byomkesh_bakshi
Type "help", "copyright", "credits" or "license" for more information.
(BetterExceptionsConsole)
>>>
```

in order to drop into a `byomkesh_bakshi`-enabled Python interactive shell.

### Advanced Usage

If you want to allow the entirety of values to be outputted instead of being truncated to a certain amount of characters:

```python
import byomkesh_bakshi
byomkesh_bakshi.MAX_LENGTH = None
```

While using `byomkesh_bakshi` in production, do not forget to unset the `BYOMKESH_BAKSHI` variable to avoid leaking sensitive data in your logs.

## Troubleshooting

If you do not see beautiful exceptions, first make sure that the environment variable does exist. You can try `echo $BYOMKESH_BAKSHI` (Linux / OSX) or `echo %BYOMKESH_BAKSHI%` (Windows). On Linux and OSX, the `export` command does not add the variable permanently, you will probably need to edit the `~/.profile` file to make it persistent. On Windows, you need to open a new terminal after the `setx` command.

Check that there is no conflict with another library, and that the `sys.excepthook` function has been correctly replaced with the `byomkesh_bakshi`'s one. Sometimes other components can set up their own exception handlers, such as the `python3-apport` Ubuntu package that you may need to uninstall.

Make sure that you have not inadvertently deleted the `byomkesh_bakshi_hook.pth` file that should be in the same place as the `byomkesh_bakshi` folder where all of your Python packages are installed. Otherwise, try re-installing `byomkesh_bakshi`.

You can also try to manually activate the hook by adding `import byomkesh_bakshi; byomkesh_bakshi.hook()` at the beginning of your script.

Finally, if you still can not get this module to work, [open a new issue](https://github.com/Qix-/better-exceptions/issues/new) by describing your problem precisely and detailing your configuration (Python and `byomkesh_bakshi` versions, OS, code snippet, interpeter, etc.) so that we can reproduce the bug you are experiencing.

# License
Copyright &copy; 2017, Josh Junon. Licensed under the [MIT license](LICENSE.txt).
