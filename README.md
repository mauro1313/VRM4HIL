# VRM4-HIL

> FPGA-based Hardware-in-the-Loop bench for a multiphase voltage regulator:
> 4-phase synchronous buck (12 V → 0.8 V, 100 A) emulated in real time on PYNQ-Z1,
> digital controller with AVP on Lattice iCE40UP5K.

![CI](https://github.com/OWNER/vrm4hil/actions/workflows/ci.yml/badge.svg)

<!-- TODO (M4): figure of the measured load step inside the TC-07 mask -->

## Architecture

<!-- TODO (M1): version of figure 2.1 from the specification -->

## Key results

| Quantity | Measured value | Test |
|---|---|---|
| Loop bandwidth and margins | — | TC-08 |
| Deviation on the 20→80 A step | — | TC-07 |
| Current imbalance (M1 set) | — | TC-10 |
| Effective DPWM resolution | — | TC-04 |
| iCE40UP5K utilization | — | TC-17 |

## Quick start

<!-- TODO (M6, DOC-04): from clone to the first co-simulation plot in < 15 minutes -->

```bash
git clone https://github.com/mauro1313/VRM4HIL && cd vrm4hil
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make help
```

## Repository map

| Folder | Contents |
|---|---|
| `docs/` | D0–D6 deliverables, ADRs, single source of truth for registers (`icd/regs.yaml`), requirements |
| `model/` | Python reference models, bit-true, project notebooks |
| `ctrl/` | controller on iCE40UP5K: RTL, board files, formal proofs, cocotb testbenches |
| `plant/` | HIL plant on PYNQ-Z1: portable core, board wrapper, Vivado scripts |
| `sw/vrm4hil/` | Python API for the plant, analysis, test runner |
| `cosim/` | closed-loop co-simulation |
| `hil/` | acceptance tests TC-01…TC-20 |
| `reports/` | generated reports (never written by hand) |
| `tools/` | tool versions, support scripts |

## Status

| Milestone | Week | Status |
|---|---|---|
| M0 Kickoff | 1 | in progress |
| M1 Modeling | 3 | — |
| M2 ICD, link, DPWM | 5 | — |
| M3 Plant v1, co-simulation | 8 | — |
| M4 First closed loop | 11 | — |
| M5 Full features | 14 | — |
| M6 Acceptance testing and release | 16 | — |

## Known limitations

The converter is emulated. The model does not include switching losses,
thermal effects (except PLT-18), parasitics beyond ESL, or magnetic nonlinearities.

## License

- **Code** (RTL, scripts, Python, build files): [Apache License 2.0](LICENSE).
- **Documentation** (text, figures, and reports in `docs/` and `reports/`): [CC BY 4.0](docs/LICENSE).

Anyone who reuses or redistributes the project must credit the authors and keep the [NOTICE](NOTICE) file.
Rationale for this choice: [ADR 0001](docs/adr/0001-license.md).

Copyright 2026 Mauro Orru and Enrico Mattana.
