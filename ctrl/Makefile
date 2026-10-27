# SPDX-FileCopyrightText: 2026 Gli autori di VRM4-HIL (vedere NOTICE)
# SPDX-License-Identifier: Apache-2.0

# Build del controllore su iCE40UP5K con la catena open source (CTL-01).
# Uso: make -C ctrl bin    oppure dalla radice: make ice40
#
# Parametri che dipendono dalla scheda (da fissare in M0 e documentare in D2):
#   PACKAGE  contenitore dell'UP5K sulla vostra scheda (sg48 per iCEBreaker e UPduino)
#   PCF      assegnazione dei pin
#   PROG     comando di programmazione

TOP     ?= top
PACKAGE ?= sg48
PCF     ?= board/board.pcf
FREQ    ?= 100
SEED    ?= 1
PROG    ?= iceprog

# rtl/: logica portabile. board/: top di scheda, PLL, SB_IO.
SRCS := $(wildcard rtl/*.v rtl/*.sv board/*.v board/*.sv)
OUT  := build

.PHONY: bin prog clean

# Ogni riga di una ricetta gira in una shell separata: il controllo e la build
# devono stare nella stessa riga, altrimenti "exit 0" non ferma nulla.
bin:
	@if [ ! -f "$(PCF)" ]; then echo "ice40: $(PCF) non esiste ancora, salto (esercizio M0)"; \
	else $(MAKE) $(OUT)/$(TOP).bin; fi

$(OUT)/$(TOP).json: $(SRCS)
	mkdir -p $(OUT)
	yosys -q -l $(OUT)/yosys.log -p "synth_ice40 -top $(TOP) -json $@" $(SRCS)

# --report scrive in JSON occupazione e frequenze massime: e' l'ingresso di TC-17.
$(OUT)/$(TOP).asc: $(OUT)/$(TOP).json $(PCF)
	nextpnr-ice40 --up5k --package $(PACKAGE) --json $< --pcf $(PCF) \
	  --freq $(FREQ) --seed $(SEED) --asc $@ \
	  --report $(OUT)/report.json -l $(OUT)/nextpnr.log

$(OUT)/$(TOP).bin: $(OUT)/$(TOP).asc
	icepack $< $@

prog: $(OUT)/$(TOP).bin
	$(PROG) $<

# TODO (M2, CTL-21): obiettivo che ripete il place-and-route su tre seed
# consecutivi e fallisce se occupazione > 80 % o margine di timing < 5 %.

clean:
	rm -rf $(OUT)
