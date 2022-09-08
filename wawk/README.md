<p align="center">
  <img src="https://wal-lang.org/static/wawk-logo.png?" alt="The Waveform AWK language logo" width="400"/>
</p>


WAWK (Waveform AWK) is a frontend to WAL inspired by the AWK text processing language.

Programs consist of multiple `condition: { action }` pairs.
The condition of each of these pairs is evaluated at each time point of the loaded waveform.
If the condition is satisfied, the statement is executed.

For example, the `basics2.wal` example in WAWK looks like this, and is executed with `wawk basics2.wawk ../basics/counter.vcd`.

```
tb.dut.clk, tb.dut.overflow: {
  print("Overflow at " + INDEX);	 
}
```

Internally, WAWK is transpiled to WAL code similar to the example below.

<p align="center">
  <img src="https://wal-lang.org/static/wawk.png?" alt="Example for transpilation from WAWK to WAL" width="600"/>
</p>

## Examples
Examples for WAWK programs can be found [here](https://github.com/ics-jku/wal/tree/main/examples/wawk).

In [this](https://github.com/LucasKl/serv-cpi) repository WAWK is used to calculate how many cycles the [SERV](https://github.com/olofk/serv) core requires for each instruction.
