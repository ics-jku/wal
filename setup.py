from setuptools import setup, find_packages
import pathlib

exec(open('wal/version.py').read())

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='wal-lang',
    version=__version__,
    description='Wal - Wavefile Analysis Language',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ics-jku/wal',
    author='Lucas Klemmer',
    author_email='lucas.klemmer@jku.at',
    classifiers=[
        'Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Operating System :: OS Independent'
    ],
    keywords=['FPGA', 'verilog', 'vcd', 'development', 'hardware', 'rtl', 'simulation', 'verification'],
    packages=find_packages(),
    python_requires='>=3.5, <4',
    install_requires=['vcdvcd==2.1', 'lark-parser'],
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
