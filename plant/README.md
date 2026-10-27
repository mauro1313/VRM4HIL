# plant

Plant HIL su PYNQ-Z1 (pipeline e timing: D; equazioni e validazione: A).

- `rtl/`: nucleo in Verilog portabile, co-simulabile con Verilator
- `board/`: involucro con IDDR/ODDR, buffer di clock, `.xdc`
- `hw/build.tcl`: progetto Vivado generato da script, nessun file di progetto in Git
- `tb/`: banchi cocotb
