from setuptools import setup, find_packages
import pathlib

from wal import __version__ as wal_version

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='wal',
    version=wal_version,
    description='Wal - Wavefile Analysis Language',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ics-jku/wal',
    author='Lucas Klemmer',
    author_email='lucas.klemmer@jku.at',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Hardware Development :: Verification Tools :: RTL Wavefiles',
        'License :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='verilog, vcd, development, hardware, rtl, simulation',
    packages=find_packages(),
    python_requires='>=3.5, <4',
    install_requires=['parsy', 'vcdvcd'],
    extras_require={
        'dev': [],
        'test': ['pylint', 'coverage'],
    },

    entry_points={
        'console_scripts': [
            'wal=wal.wal:run',
            'walc=wal.walc:run'
        ],
    },
)
