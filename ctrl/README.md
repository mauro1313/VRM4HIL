# ctrl

Controller on iCE40UP5K (owner D). Build: `make -C ctrl bin` or `make ice40` from the root.

- `rtl/`: portable logic (no device primitives)
- `board/`: board top, PLL, SB_IO, `.pcf` file
- `formal/`: `.sby` files and properties P1–P7
- `tb/`: one cocotb testbench per subfolder
