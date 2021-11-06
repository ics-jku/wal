cfg:
	wawk -f cfg.wawk gcd.vcd > cfg.dot
	dot cfg.dot -o cfg.png -Tpng
	eog cfg.png
	rm cfg.png cfg.dot

text:
	wawk -f cfg2.wawk gcd2.vcd
