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
    version=__version__,
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
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
        'Operating System :: OS Independent'
    ],
    keywords=['verilog', 'vcd', 'fst', 'development', 'hardware', 'rtl', 'simulation', 'verification', 'FPGA'],
    packages=find_packages(),
    python_requires='>=3.7, <4',
    install_requires=['vcdvcd==2.1', 'lark-parser', 'dataclasses', 'pylibfst'],
    extras_require={
        'dev': [],
        'test': ['pylint', 'coverage'],
    },

    entry_points={
        'console_scripts': [
            'wal=wal.wal:run',
            'walc=wal.walc:run',
            'wawk=wawk.wawk:run'
        ],
    },
)
