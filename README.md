# WAL the Waveform Analysis Language
[![Pylint](https://github.com/ics-jku/wal/actions/workflows/pylint.yml/badge.svg)](https://github.com/ics-jku/wal/actions/workflows/pylint.yml)
[![Test and Build](https://github.com/ics-jku/wal/actions/workflows/python-app.yml/badge.svg)](https://github.com/ics-jku/wal/actions/workflows/python-app.yml)

<p align="center">
  <img src="https://wal-lang.org/static/logo.svg?" alt="The Waveform Analysis language logo" width="200"/>
</p>

Welcome to the Waveform Analysis Language (WAL) repository. This domain-specific language aims at enabling automated and sophisticated analysis of hardware waveforms. In WAL, hardware-specific things such as signals and simulation time are treated as first-class citizens of the language.

## Installation from PyPi
WAL is available from [PyPi](https://pypi.org/project/wal-lang/)!
> pip install wal-lang --user

On some systems, pip does not add WALs installation path to the PATH variable. If the "wal" command is not available after installation please add the installation path, e.g. ~/.local/bin on Ubuntu, to your PATH variable.

To get the latest development version of WAL you can clone this repository.
After that, follow the instructions for your OS below inside the cloned directory.

## Installation from Source
For Ubuntu (22.04 LTS):
```
sudo apt install git cmake python3-cffi python3.10-venv python3-pip build-essential
git clone https://github.com/ics-jku/wal.git
cd wal
pip install build virtualenv
make install
echo "export PATH=\$PATH:$HOME/.local/bin" >> ~/.bashrc
```

For Fedora (36):
```
sudo dnf install git cmake g++ zlib-devel python3-devel
git clone https://github.com/ics-jku/wal.git
cd wal
pip install build virtualenv
make install
```

For OpenSuse Tumbleweed:
```
sudo zypper install git cmake gcc-c++ zlib-devel python3-devel
git clone https://github.com/ics-jku/wal.git
cd wal
pip install build virtualenv
make install
```

### PyPy and Pyston Support
WAL also supports the alternative Python implementations PyPy and Pyston.
Both alternative implementations can lead to substantial speedups in a lot of scenarios.
To install WAL with an alternative implementation change the *PYTHON* variable in the Makefile or install with `PYTHON=pypy3 make install`.

If you are using PyPy you must also have the python-dev package installed for PyPy3.
On Ubuntu this package can be installed with 'sudo apt install pypy3-dev'.

## Documentation
The WAL Programmer Manual is available on [wal-lang.org](https://wal-lang.org/documentation/core).

## Examples
To get an impression of WAL you can check out [basic examples](https://github.com/ics-jku/wal/tree/main/examples/basics).
Also, this ASCII cast [ASCII Cast](https://asciinema.org/a/I8fQknySyaZqNjXAA8Ej7wOoq), shows how the WAL REPL is used to compare two RISCV cores.

A more sophisticated RISC-V core comparison is described [here](https://www.ics.jku.at/files/2022DAC_LBR-Waveform-based-Performance-Analyisis-for-RISC-V.pdf) and the WAL code to this publication can be found [here](https://github.com/LucasKl/dac22-lbr-experiments).

### WAWK
[WAWK](https://github.com/ics-jku/wal/tree/main/wawk) is a project building on top of the WAL language. It combines the waveform analysis of WAL with the programming Style of AWK.
Internally, WAWK is transpiled to WAL expressions, showcasing how new languages can be build on top of WAL.

## Publication
The initial paper on WAL was presented at ASPDAC'22 and can be downloaded here: https://www.ics.jku.at/files/2022ASPDAC_WAL.pdf.
The examples from the paper can be found in the *examples* folder.

If you like WAL you can cite our paper as follows:

```
@InProceedings{KG:2022,
  author        = {Lucas Klemmer and Daniel Gro{\ss}e},
  title         = {{WAL:} A Novel Waveform Analysis Language for Advanced Design Understanding and Debugging},
  booktitle     = {ASP Design Automation Conf.},
  year          = 2022
}

```

## Emacs Mode
A basic major mode for Emacs is available [here](https://github.com/LucasKl/wal-major-mode).
