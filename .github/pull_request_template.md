## What changes and why

<!-- One or two sentences. Link the issue: "Closes #NN". Requirements touched: CTL-xx, PLT-xx... -->

## How it was verified

<!-- Tests added or modified, command to rerun them, outcome. -->

## Checklist (Appendix D.4)

- [ ] The change has a test that would fail without it
- [ ] RTL: reset of the registers that need it, no inferred latches
- [ ] RTL: clock-domain crossings only through synchronizers or FIFOs
- [ ] RTL: widths and fixed-point formats declared at the top of the module
- [ ] No new linter warnings
- [ ] Bit-true model updated in the same commit as the RTL
- [ ] Timing and utilization not worsened beyond the agreed threshold (CI summary)
- [ ] Python: units in the names, no hardcoded values
- [ ] Documentation and `docs/icd/regs.yaml` updated if visible behavior changes
- [ ] If the ICD changes: ICD revision approved by A and D
