# Convenzioni di repository e di codice

Parte del deliverable D0. Le voci marcate **DECISIONE** vanno chiuse in M0:
ognuna si risolve con una frase di motivazione, oppure con una ADR se non è ovvia.

## Git

- Ramo principale `main`, protetto: pull request obbligatoria, CI verde, una revisione approvata dall'altro (regola dei quattro occhi). Revisione entro 48 ore.
- Un ramo per issue: `area/breve-descrizione`, per esempio `ctrl/dpwm-pipeline`.
- Messaggi di commit: `area: azione`, per esempio `ctrl/dpwm: registra il confronto un ciclo prima`.
- Aree: `ctrl`, `plant`, `model`, `sw`, `cosim`, `hil`, `docs`, `ci`, `tools`.
- Nessun file generato in Git: bitstream, progetti Vivado, cartelle di simulazione. I bitstream di collaudo si allegano alle release con tag.

## RTL

- **DECISIONE (D):** dialetto. Verilog-2005 puro oppure il sottoinsieme di SystemVerilog accettato da Yosys (CTL-01)? Che cosa vi serve davvero di SV, e che cosa vi costa nella portabilità fra Yosys, Verilator, Icarus e Vivado?
- **DECISIONE (D):** reset. Sincrono o asincrono, attivo alto o basso, e quali registri ne hanno bisogno. Rileggete la nota del committente nel § 14.1 sul percorso critico residuo prima di rispondere.
- Un modulo per file, nome del file uguale al nome del modulo.
- Suffisso del dominio di clock su ogni segnale dove c'è più di un dominio: `_sys`, `_sclk`.
- Nessun numero magico: parametri da `localparam` con l'unità nel nome (`DEADTIME_NS`, `TSW_CYCLES`) o da costanti generate da `docs/icd/regs.yaml`.
- `default_nettype none` in testa a ogni file.
- Le primitive di dispositivo (`SB_PLL40_*`, `SB_IO`, `IDDR`, `ODDR`...) solo in `*/board/`. In `*/rtl/` solo logica portabile, simulabile e lintabile da sola.

### Intestazione di ogni modulo

```verilog
// SPDX-FileCopyrightText: 2026 Gli autori di VRM4-HIL (vedere NOTICE)
// SPDX-License-Identifier: Apache-2.0
// -----------------------------------------------------------------------------
// Modulo   : nome_modulo
// Funzione : una frase
// Clock    : clk_sys (100 MHz)          Reset: <come deciso sopra>
// Latenza  : N cicli dall'ingresso X all'uscita Y
// Ingressi : x  Q1.15  (unità)
// Uscite   : y  Q4.12  (unità), saturata
// Requisiti: CTL-xx, CTL-yy
// -----------------------------------------------------------------------------
`default_nettype none
```

## Virgola fissa

- Notazione `Qm.n`: m bit interi segno compreso, n bit frazionari. Si scrive il formato di ogni segnale nel codice e nella documentazione.
- Arrotondamento al più vicino dove il troncamento introdurrebbe deriva (integratori).
- Aritmetica saturante sulle uscite di ogni stadio, con contatore di saturazioni leggibile.

## Python

- Python 3.12, `ruff` per lo stile.
- Unità nei nomi: `t_dead_ns`, `i_load_a`, `v_out_v`.
- Modelli bit-true con interi Python e maschere esplicite: nessun `float` nel percorso.
- Il modello bit-true di un modulo lo scrive chi non ne ha scritto l'RTL (§ 20.2).

## Documentazione

- Ogni cartella ha un README di poche righe.
- Decisioni non ovvie in `docs/adr/NNNN-titolo.md` (modello: `0000-template.md`).

## Licenze

Scelta motivata in [ADR 0001](adr/0001-licenza.md).

- Codice: Apache-2.0. Ogni file sorgente nuovo (`.v`, `.sv`, `.py`, `.tcl`, `.sby`, `Makefile`, `.yaml`, `.pcf`, `.xdc`) inizia con le due righe SPDX, nel commento del proprio linguaggio (`//` per Verilog, `#` per Python, Tcl, Make, YAML e PCF). Negli script con shebang vanno subito dopo la prima riga.

  ```
  SPDX-FileCopyrightText: 2026 Gli autori di VRM4-HIL (vedere NOTICE)
  SPDX-License-Identifier: Apache-2.0
  ```

- Documentazione, figure e report: CC BY 4.0 (`docs/LICENSE`), senza intestazione nei singoli file.
- Materiale di terzi (per esempio il file XDC di Digilent o esempi di vendor): si conserva l'intestazione originale, non si aggiunge la nostra, e si annota in `NOTICE` con la sua licenza. Gli IP Xilinx non si committano: si rigenerano dagli script Tcl (VER-07).
- Nessun materiale coperto da accordi di riservatezza (§ 1.5).
