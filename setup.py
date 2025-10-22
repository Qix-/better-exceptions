"""Setup script for better_exceptions - handles .pth file installation"""
from os.path import basename, dirname, join
from setuptools import setup
from setuptools.command.build import build


class BuildWithPTH(build):
    def run(self):
        build.run(self)
        path = join(dirname(__file__), 'better_exceptions_hook.pth')
        dest = join(self.build_lib, basename(path))
        self.copy_file(path, dest)


# Metadata is in pyproject.toml, this only handles .pth installation
setup(
    cmdclass={
        'build': BuildWithPTH,
    }
)
