<div align="center">![alt text](icon.png "WAL Icon")</div>
<div align="center"><h3>WAL</h3></div>
<div align="center">AWK style wavefile analysis</div>


[![build_status](https://gitlab.ics.jku.at/klemmer/wal/badges/master/pipeline.svg)](https://gitlab.ics.jku.at/klemmer/wal/commits/master)
[![coverage report](https://gitlab.ics.jku.at/klemmer/wal/badges/master/coverage.svg)](https://gitlab.ics.jku.at/klemmer/wal/commits/master)


## Idea


i_valid: ▁▁▁▁▁▁▁▁▁▁▁╱▔▔▔▔╲▁▁▁▁▁▁▁

i_ready: ▁▁▁▁▁▁▁╱▔▔▔▔▔▔▔▔╲▁▁▁▁▁▁▁

i_data : ▁▁▁▁▁▁▁▁▁▁▁╱ 43 ╲▁▁▁▁▁▁▁

Find all bus transaction and print the payload.
```lisp
i_valid, i_ready: (print i_data)
```

Sum the number of cycles spend waiting for ready signal.
```lisp
i_valid, (! i_ready): (set wait (+ wait 1))

END: (print "Waited " wait " cycles")
```

```
@STRING{aspdac	= {ASP Design Automation Conf.} }
@InProceedings{KG:2022,
  author        = {Lucas Klemmer and Daniel Gro{\ss}e},
  title         = {{WAL:} A Novel Waveform Analysis Language for Advanced Design Understanding and Debugging},
  booktitle     = aspdac,
  year          = 2022
}

```