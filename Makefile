# VRM4-HIL - Makefile di radice.
# Ogni artefatto della repository si rigenera con uno di questi obiettivi (VER-07).
# Gli obiettivi senza sorgenti avvisano e terminano senza errore: in M0 la CI
# deve essere verde anche sullo scheletro. Quando un'area ha i suoi sorgenti,
# il controllo diventa reale.

SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c

CTRL_RTL   := $(wildcard ctrl/rtl/*.v ctrl/rtl/*.sv)
PLANT_RTL  := $(wildcard plant/rtl/*.v plant/rtl/*.sv)
TB_DIRS    := $(patsubst %/Makefile,%,$(wildcard ctrl/tb/*/Makefile plant/tb/*/Makefile))
SBY_FILES  := $(wildcard ctrl/formal/*.sby)

.PHONY: help lint test formal ice40 prog pytest hw report docs clean

help:  ## elenca gli obiettivi
	@grep -E '^[a-z0-9_-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-10s %s\n", $$1, $$2}'

lint:  ## lint dell'RTL portabile (solo rtl/, mai board/: le primitive di scheda restano fuori)
	@if [ -z "$(strip $(CTRL_RTL) $(PLANT_RTL))" ]; then echo "lint: nessun sorgente in */rtl, salto"; exit 0; fi
	for f in $(CTRL_RTL) $(PLANT_RTL); do
	  echo "lint: $$f"
	  verilator --lint-only -Wall -Wno-DECLFILENAME "$$f"
	done

test:  ## test unitari cocotb: una sottocartella per banco in ctrl/tb e plant/tb
	@if [ -z "$(strip $(TB_DIRS))" ]; then echo "test: nessun banco cocotb, salto"; exit 0; fi
	for d in $(TB_DIRS); do
	  echo "test: $$d"
	  rm -f "$$d/results.xml"
	  $(MAKE) -C "$$d"
	  # Non ci si fida del solo codice d'uscita: si controlla il file dei risultati.
	  test -f "$$d/results.xml" || { echo "test: $$d non ha prodotto results.xml"; exit 1; }
	  if grep -q "<failure" "$$d/results.xml"; then echo "test: FALLITO in $$d"; exit 1; fi
	done

formal:  ## prove formali SymbiYosys (tutte le task di ogni .sby)
	@if [ -z "$(strip $(SBY_FILES))" ]; then echo "formal: nessun file .sby, salto"; exit 0; fi
	for f in $(SBY_FILES); do
	  echo "formal: $$f"
	  (cd "$$(dirname $$f)" && sby -f "$$(basename $$f)")
	done

ice40:  ## sintesi, place-and-route e bitstream del controllore
	$(MAKE) -C ctrl bin

prog:  ## programma la scheda iCE40
	$(MAKE) -C ctrl prog

pytest:  ## test Python dei modelli e del software
	# pytest restituisce 5 se non trova test: in M0 e' normale, non un errore.
	pytest model sw || [ $$? -eq 5 ]

hw:  ## bitstream del plant con Vivado (richiede Vivado 2024.1 installato)
	@test -f plant/hw/build.tcl || { echo "hw: plant/hw/build.tcl non esiste ancora"; exit 1; }
	vivado -mode batch -source plant/hw/build.tcl -tclargs --out build/plant

report:  ## report di collaudo D5 dai file di risultati (M6)
	@echo "report: da scrivere (VER-06, DOC-03)"; exit 1

docs:  ## documentazione generata da docs/icd/regs.yaml (M2)
	@echo "docs: da scrivere (IF-06)"; exit 1

clean:  ## elimina gli output generati
	rm -rf build ctrl/build
	find . -name sim_build -type d -prune -exec rm -rf {} +
	find . -name results.xml -delete
