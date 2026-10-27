# ctrl

Controllore su iCE40UP5K (responsabile D). Build: `make -C ctrl bin` o `make ice40` dalla radice.

- `rtl/`: logica portabile (niente primitive del dispositivo)
- `board/`: top di scheda, PLL, SB_IO, file `.pcf`
- `formal/`: file `.sby` e proprietà P1–P7
- `tb/`: un banco cocotb per sottocartella
