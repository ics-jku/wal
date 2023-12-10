'''Setup file for the wal-lang package'''
# pylint: disable=W0122,E0602
import pathlib
from setuptools import setup, find_packages

with open('wal/version.py', encoding="utf8") as f:
    exec(f.read())

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='wal-lang',
    version=__version__, # noqa: F821
    description='Wal - Wavefile Analysis Language',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://wal-lang.org',
    author='Lucas Klemmer',
    author_email='support@wal-lang.org',
    classifiers=[
        'Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3 :: Only',
        'Operating System :: OS Independent'
    ],
    keywords=['verilog', 'VHDL', 'vcd', 'fst', 'development', 'hardware', 'rtl', 'simulation', 'verification', 'FPGA'],
    packages=find_packages(),
    python_requires='>=3.9, <4',
    install_requires=['lark'],
    extras_require={
        'dev': [],
        'test': ['ruff', 'coverage'],
    },
    package_data={
        'wal': ['libs/std/std.wal', 'libs/std/std.wo', 'libs/std/module.wal', 'libs/std/module.wo']
    },

    entry_points={
        'console_scripts': [
            'wal=wal.wal:run',
            'walc=wal.walc:run',
            'wawk=wawk.wawk:run',
        ],
    },
)
