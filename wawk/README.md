# WAWK

WAWK (Waveform AWK) is a frontend to WAL inspired by the AWK text processing language.

Programs consist of multiple `condition: statement` pairs.
The condition of each of these pairs is evaluated at each time point of the loaded waveform.
If the condition is satisfied, the statement is executed.

For example, the `basics2.wal` example in WAWK looks like this.

```
tb.dut.clk, tb.dut.overflow: {
  print("Overflow at " + INDEX);	 
}
```

And is executed with `wawk basics2.wawk ../basics/counter.vcd`.

## Examples
Examples for WAWK programs can be found [here](https://github.com/ics-jku/wal/tree/main/examples/wawk).

In [this](https://github.com/LucasKl/serv-cpi) repository WAWK is used to calculate how many cycles the [SERV](https://github.com/olofk/serv) core requires for each instruction.
