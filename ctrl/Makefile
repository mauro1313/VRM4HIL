# SPDX-FileCopyrightText: 2026 VRM4-HIL authors (see NOTICE)
# SPDX-License-Identifier: Apache-2.0

# Build of the controller on iCE40UP5K with the open source toolchain (CTL-01).
# Usage: make -C ctrl bin    or from the root: make ice40
#
# Board-dependent parameters (to be fixed in M0 and documented in D2):
#   PACKAGE  UP5K package on your board (sg48 for iCEBreaker and UPduino)
#   PCF      pin assignment
#   PROG     programming command

TOP     ?= top
PACKAGE ?= sg48
PCF     ?= board/board.pcf
FREQ    ?= 100
SEED    ?= 1
PROG    ?= iceprog

# rtl/: portable logic. board/: board top, PLL, SB_IO.
SRCS := $(wildcard rtl/*.v rtl/*.sv board/*.v board/*.sv)
OUT  := build

.PHONY: bin prog clean

# Each recipe line runs in a separate shell: the check and the build
# must be on the same line, otherwise "exit 0" does not stop anything.
bin:
	@if [ ! -f "$(PCF)" ]; then echo "ice40: $(PCF) does not exist yet, skipping (M0 exercise)"; \
	else $(MAKE) $(OUT)/$(TOP).bin; fi

$(OUT)/$(TOP).json: $(SRCS)
	mkdir -p $(OUT)
	yosys -q -l $(OUT)/yosys.log -p "synth_ice40 -top $(TOP) -json $@" $(SRCS)

# --report writes utilization and max frequencies in JSON: it is the input to TC-17.
$(OUT)/$(TOP).asc: $(OUT)/$(TOP).json $(PCF)
	nextpnr-ice40 --up5k --package $(PACKAGE) --json $< --pcf $(PCF) \
	  --freq $(FREQ) --seed $(SEED) --asc $@ \
	  --report $(OUT)/report.json -l $(OUT)/nextpnr.log

$(OUT)/$(TOP).bin: $(OUT)/$(TOP).asc
	icepack $< $@

prog: $(OUT)/$(TOP).bin
	$(PROG) $<

# TODO (M2, CTL-21): target that repeats place-and-route over three
# consecutive seeds and fails if utilization > 80% or timing margin < 5%.

clean:
	rm -rf $(OUT)
