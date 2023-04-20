# -*- coding: utf-8 -*-

import subprocess  # nosec
import sys

import setuptools

# version string
__version__ = '0.16.3'

# README
with open('README.rst', encoding='utf-8') as file:
    long_description = file.read()

###############################################################################
# general configuration
###############################################################################

# setup attributes
attrs = dict(
    name='pypcapkit',
    version=__version__,
    description='Comprehensive Network Packet Analysis Library',
    long_description=long_description,
    author='Jarry Shaw',
    author_email='jarryshaw@icloud.com',
    maintainer='Jarry Shaw',
    maintainer_email='jarryshaw@icloud.com',
    url='https://github.com/JarryShaw/PyPCAPKit',
    download_url='https://github.com/JarryShaw/PyPCAPKit/archive/v%s.tar.gz' % __version__,  # pylint: disable=consider-using-f-string
    # py_modules
    packages=setuptools.find_packages(),
    # scripts
    # ext_modules
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: System :: Networking',
        'Topic :: Utilities',
        'Typing :: Typed',
    ],
    # distclass
    # script_name
    # script_args
    # options
    license='BSD 3-Clause License',
    keywords=[
        'computer-networking',
        'pcap-analyser',
        'pcap-parser',
    ],
    platforms=[
        'any'
    ],
    # cmdclass
    # data_files
    # package_dir
    # obsoletes
    # provides
    # requires
    # command_packages
    # command_options
    package_data={
        '': [
            'LICENSE',
            'README.rst',
        ],
    },
    # include_package_data
    # libraries
    # headers
    # ext_package
    # include_dirs
    # password
    # fullname
    # long_description_content_type
    # python_requires
    # zip_safe
    install_requires=[
        'dictdumper~=0.8.0',        # for formatted output
        'chardet',                  # for bytes decode
        'aenum',                    # for const types
        'tbtrim>=0.2.1',            # for refined exceptions
    ],
    entry_points={
        'console_scripts': [
            'pcapkit-cli = pcapkit.__main__:main',
            'pcapkit-vendor = pcapkit.vendor.__main__:main',
        ]
    },
    extras_require={
        'all': [
            'emoji',
            'dpkt', 'scapy', 'pyshark',
            'requests[socks]', 'beautifulsoup4[html5lib]',
        ],
        # for CLI display
        'cli': ['emoji'],
        # for normal users
        'DPKT': ['dpkt'],
        'Scapy': ['scapy'],
        'PyShark': ['pyshark'],
        # for developers
        'vendor': ['requests[socks]', 'beautifulsoup4[html5lib]'],
    },
    setup_requires=[
        # version compatibility
        'f2format; python_version < "3.6"',
        'bpc-walrus; python_version < "3.8"',
        'pathlib2>=2.3.2; python_version == "3.4"',
    ],
)

###############################################################################
# pybpc integration
###############################################################################


def refactor() -> 'None':
    """Refactor code."""
    if version_info < (3, 6):
        try:
            subprocess.check_call(  # nosec
                [sys.executable, '-m', 'f2format', '--no-archive', 'pcapkit']
            )
        except subprocess.CalledProcessError as error:
            print('Failed to perform assignment expression backport compiling.'
                  'Please consider manually install `bpc-f2format` and try again.', file=sys.stderr)
            sys.exit(error.returncode)

    if version_info < (3, 8):
        try:
            subprocess.check_call(  # nosec
                [sys.executable, '-m', 'walrus', '--no-archive', 'pcapkit']
            )
        except subprocess.CalledProcessError as error:
            print('Failed to perform assignment expression backport compiling.'
                  'Please consider manually install `bpc-walrus` and try again.', file=sys.stderr)
            sys.exit(error.returncode)


###############################################################################
# setuptools commands
###############################################################################

from setuptools import setup
from setuptools.command.bdist_egg import bdist_egg as _bdist_egg
from setuptools.command.build_py import build_py as _build_py
from setuptools.command.develop import develop as _develop
from setuptools.command.install import install as _install
from setuptools.command.sdist import sdist as _sdist

version_info = sys.version_info[:2]

attrs.update(dict(
    include_package_data=True,
    # libraries
    # headers
    # ext_package
    # include_dirs
    # password
    # fullname
    long_description_content_type='text/x-rst',
    python_requires='>=3.6',
    zip_safe=True,
))


class bdist_egg(_bdist_egg):
    """Add on-distribution backport code conversion."""

    def run(self) -> 'None':
        """Run command."""
        refactor()
        _bdist_egg.run(self)


class develop(_develop):
    """Add on-develop backport code conversion."""

    def run(self) -> 'None':
        """Run command."""
        refactor()
        _develop.run(self)


class build_py(_build_py):
    """Add on-build backport code conversion."""

    def run(self) -> 'None':
        refactor()
        _build_py.run(self)


class install(_install):
    """Add on-install backport code conversion."""

    def run(self) -> 'None':
        refactor()
        _install.run(self)


class sdist(_sdist):
    """Add on-distribution backport code conversion."""

    def run(self) -> 'None':
        refactor()
        _sdist.run(self)


cmdclass = {
    'bdist_egg': bdist_egg,
    'develop': develop,
}

###############################################################################
# wheel commands
###############################################################################

try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel


    class bdist_wheel(_bdist_wheel):
        """Add on-wheel backport code conversion."""

        def run(self) -> 'None':
            """Run command."""
            refactor()
            _bdist_wheel.run(self)


    cmdclass['bdist_wheel'] = bdist_wheel
except ImportError:
    pass

###############################################################################
# final setup
###############################################################################

# set-up script for pip distribution
setup(cmdclass={
    'build_py': build_py,
    'install': install,
    'sdist': sdist,
    **cmdclass,
}, **attrs)
