# WAL the Waveform Analysis Language
[![Test and Build](https://github.com/ics-jku/wal/actions/workflows/python-app.yml/badge.svg)](https://github.com/ics-jku/wal/actions/workflows/python-app.yml)

<p align="center">
  <img src="https://wal-lang.org/static/logo.svg?" alt="The Waveform Analysis language logo" width="200"/>
</p>

WAL, the Waveform Analysis Language, enables automated and fast analysis of hardware waveforms. In WAL, hardware-specific things such as signals and simulation time are treated as first-class citizens of the language.

## Interactive Tutorial
Try out WAL without installation using our [interactive tutorial](https://app.wal-lang.org/).

## Installation from PyPi
WAL is available from [PyPi](https://pypi.org/project/wal-lang/)!
> pip install wal-lang --user

On some systems, pip does not add WALs installation path to the PATH variable. If the "wal" command is not available after installation please add the installation path, e.g. ~/.local/bin on Ubuntu, to your PATH variable.

To get the latest development version of WAL you can clone this repository.
After that, follow the instructions for your OS below inside the cloned directory.

## Installation from Source
For Ubuntu:
```
sudo apt install git cmake python3-cffi python3.10-venv python3-pip build-essential -y
git clone https://github.com/ics-jku/wal.git
cd wal
PYTHON=python3 make install
echo "export PATH=\$PATH:$HOME/.local/bin" >> ~/.bashrc
```

For Fedora:
```
sudo dnf install git cmake g++ zlib-devel python3-devel -y
git clone https://github.com/ics-jku/wal.git
cd wal
make install
```

For OpenSuse Tumbleweed:
```
sudo zypper install git cmake gcc-c++ zlib-devel python3-devel
git clone https://github.com/ics-jku/wal.git
cd wal
make install
```

### Support for fst waveforms
To add support for the fst filetype to WAL, install the `pylibfst` package.
```
pip install --user pylibfst
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

### WAWK
[WAWK](https://github.com/ics-jku/wal/tree/main/wawk) is a project building on top of the WAL language. It combines the waveform analysis of WAL with the programming Style of AWK.
Internally, WAWK is transpiled to WAL expressions, showcasing how new languages can be build on top of WAL.

## Publications
The initial paper on WAL was presented at ASPDAC'22 and can be downloaded [here](https://www.ics.jku.at/files/2022ASPDAC_WAL.pdf).
The examples from the paper can be found in the *examples* folder.

An extended open-access journal article about WAL is available [here](https://ieeexplore.ieee.org/document/10496480).

If you found WAL useful for your research, please consider citing on of our papers:

```
@ARTICLE{10496480,
  author={Klemmer, Lucas and Große, Daniel},
  journal={IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems},
  title={WAVING Goodbye to Manual Waveform Analysis in HDL Design With WAL},
  year={2024},
  volume={43},
  number={10},
  pages={3198-3211},
  doi={10.1109/TCAD.2024.3387312}}
```

```
@InProceedings{KG:2022,
  author        = {Lucas Klemmer and Daniel Gro{\ss}e},
  title         = {{WAL:} A Novel Waveform Analysis Language for Advanced Design Understanding and Debugging},
  booktitle     = {ASP Design Automation Conf.},
  year          = 2022
}

```

WAL was also used in other publications for [processor analysis](https://doi.org/10.1145/3489517.3530623), [Spade HDL integration](https://doi.org/10.1109/FDL59689.2023.10272204), [pipeline visualization](https://ics.jku.at/files/2023RISCVSummit_DSLforVisualizingPipelines.pdf), and for a novel [debug methodology](https://ics.jku.at/files/2024ASPDAC_WAL-VirtualSignals.pdf).

## Emacs Mode
A basic major mode for Emacs is available [here](https://github.com/LucasKl/wal-major-mode).
