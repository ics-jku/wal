# RISC-V Function Profiling from Waveforms

This example implements a function-level RISC-V profiler that extracts the time spent in each function out of a simulation waveform.
The profiler program consists of a single Python script that accesses and analyzes the waveform data using the [Waveform Analysis Language](https://github.com/ics-jku/wal). It is not tied to any particular RISC-V core and can be easily adapted to new cores over a single configuration file.

The main project of the script can be found [here](https://github.com/LucasKl/riscv-function-profiling).

## Profiling Waveforms
To profile a waveform you need to have a RISC-V elf binary and a vcd waveform of a RISC-V core running the binary.
Profiling is started py running the Python script with the elf file as the first and the vcd file as the second argument.

The example can be run by typing `python profile.py gcd.elf ../wawk/basic-blocks/gcd.vcd` in this directory.

## How does it work?
This program extracts information about the functions from the elf file using the "nm" command. This command prints a list of all symbols and their sizes*.
Using this information the start and end addresses of functions are calculated. Then, the WAL code, which is embedded into the main script similar to SQL query, searches the waveform for all executed instructions and their location in the binary. The location is then compared to the function address ranges and a counter for the function that is associated with this address is incremented.