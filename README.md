# WAL the Waveform Analysis Language
[![Pylint](https://github.com/ics-jku/wal/actions/workflows/pylint.yml/badge.svg)](https://github.com/ics-jku/wal/actions/workflows/pylint.yml)
[![Test and Build](https://github.com/ics-jku/wal/actions/workflows/python-app.yml/badge.svg)](https://github.com/ics-jku/wal/actions/workflows/python-app.yml)

      ┌─┐ ┌─┐ ┌─┐ 
     ─┘W└─┘A└─┘L└─
     
Welcome to the Waveform Analysis Language (WAL) repository. This domain-specific language aims at enabling automated and sophisticated analysis of hardware waveforms. In WAL, hardware-specific things such as signals and simulation time are treated as first-class citizens.

## Installation
WAL is available from PyPi!                                                                                                                                                         
> pip install wal-lang --user

On some systems, pip does not add WALs installation path to the PATH variable. If the "wal" command is not available after installation please add the installation path, e.g. ~/.local/bin on Ubuntu, to your PATH variable.       

To get the latest development version of WAL you can clone this repository.
After that install WAL by typing make install inside the cloned directory.       

### Example
To get an impression of WAL you can check out this ASCII cast [ASCII Cast](https://asciinema.org/a/I8fQknySyaZqNjXAA8Ej7wOoq), in which the WAL REPL is used to compare two RISCV cores.

## Publication
The initial paper on WAL was presented at ASPDAC'22 and can be downloaded here: https://www.ics.jku.at/files/2022ASPDAC_WAL.pdf. 
The examples from the paper can be found in the examples folder.

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
