# VRM4-HIL

> Banco Hardware-in-the-Loop su FPGA per un regolatore di tensione multifase:
> buck sincrono a 4 fasi (12 V → 0,8 V, 100 A) emulato in tempo reale su PYNQ-Z1,
> controllore digitale con AVP su Lattice iCE40UP5K.

![CI](https://github.com/OWNER/vrm4hil/actions/workflows/ci.yml/badge.svg)

<!-- TODO (M4): figura del gradino di carico misurato dentro la maschera di TC-07 -->

## Architettura

<!-- TODO (M1): versione della figura 2.1 del capitolato -->

## Risultati principali

| Grandezza | Valore misurato | Test |
|---|---|---|
| Banda e margini dell'anello | — | TC-08 |
| Deviazione al gradino 20→80 A | — | TC-07 |
| Squilibrio di corrente (set M1) | — | TC-10 |
| Risoluzione efficace del DPWM | — | TC-04 |
| Occupazione iCE40UP5K | — | TC-17 |

## Avvio rapido

<!-- TODO (M6, DOC-04): dalla clonazione al primo grafico di co-simulazione in < 15 minuti -->

```bash
git clone https://github.com/mauro1313/VRM4HIL && cd vrm4hil
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make help
```

## Mappa della repository

| Cartella | Contenuto |
|---|---|
| `docs/` | deliverable D0–D6, ADR, sorgente unica dei registri (`icd/regs.yaml`), requisiti |
| `model/` | modelli Python di riferimento, bit-true, notebook di progetto |
| `ctrl/` | controllore su iCE40UP5K: RTL, file di scheda, prove formali, banchi cocotb |
| `plant/` | plant HIL su PYNQ-Z1: nucleo portabile, involucro di scheda, script Vivado |
| `sw/vrm4hil/` | API Python del plant, analisi, test runner |
| `cosim/` | co-simulazione ad anello chiuso |
| `hil/` | test di accettazione TC-01…TC-20 |
| `reports/` | report generati (mai scritti a mano) |
| `tools/` | versioni dei tool, script di supporto |

## Stato

| Milestone | Settimana | Stato |
|---|---|---|
| M0 Avvio | 1 | in corso |
| M1 Modellazione | 3 | — |
| M2 ICD, link, DPWM | 5 | — |
| M3 Plant v1, co-simulazione | 8 | — |
| M4 Primo anello chiuso | 11 | — |
| M5 Funzioni complete | 14 | — |
| M6 Collaudo e release | 16 | — |

## Limiti noti

Il convertitore è emulato. Il modello non contiene perdite di commutazione,
effetti termici (salvo PLT-18), parassiti oltre l'ESL, non linearità magnetiche.

## Licenza

<!-- TODO: Apache-2.0 o MIT, scelta in M0 -->
