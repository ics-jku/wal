from setuptools import setup, find_packages
import pathlib

from wawk import __version__ as wawk_version

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='wawk',
    version=wawk_version,
    description='wawk - AWK inspired wavefile analysis',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ics-jku/wal',
    author='Lucas Klemmer',
    author_email='lucas.klemmer@jku.at',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Hardware Development :: Verification Tools :: RTL Wavefiles',
        'License :: BSD 3-Clause License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='verilog, vcd, development, hardware, rtl, awk, simulation',
    packages=find_packages(),
    python_requires='>=3.5, <4',
    install_requires=['wal', 'lark'],
    extras_require={
        'dev': [],
        'test': ['pylint', 'coverage'],
    },

    entry_points={
        'console_scripts': [
            'wawk=wawk.wawk:run'
        ],
    },
)
