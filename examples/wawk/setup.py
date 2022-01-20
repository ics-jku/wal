from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / 'README.md').read_text(encoding='utf-8')

exec(open('wawk/version.py').read())

setup(
    name='wawk-lang',
    version=__version__,
    description='wawk - AWK inspired wavefile analysis',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ics-jku/wal',
    author='Lucas Klemmer',
    author_email='lucas.klemmer@jku.at',
    classifiers=[
        'Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)',
        'Development Status :: 3 - Alpha',
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
    install_requires=['wal-lang'],
    entry_points={
        'console_scripts': [
            'wawk=wawk.wawk:run'
        ],
    },
)
