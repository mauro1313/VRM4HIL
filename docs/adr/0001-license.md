# 0001. Project licenses

- Status: proposed
- Date: 2026-10-27
- Authors: A, D
- Requirements: § 1.5 (intellectual property), § 7.9 criterion 5

## Context

The specification requires a public repository with an open source license of our choice, with Apache-2.0 or MIT recommended. The repository contains code (Verilog RTL for iCE40 and Zynq, Python, build scripts) and documentation (D0–D6 deliverables, figures, reports). It does not contain PCB designs: the boards are commercial.

The project is a demonstrator, but we want anyone who reuses it to credit the authors and to keep it clear which parts are ours.

## Alternatives considered

1. **MIT for everything**: very short text, maximum reach. Only requires keeping the copyright notice. Says nothing about patents or modifications and does not distinguish code from text.
2. **Apache-2.0 for the code, CC BY 4.0 for the documentation**: as permissive as MIT. It additionally requires keeping the NOTICE file and flagging modified files, grants an explicit patent license, and excludes trademarks. CC BY is the reference license for text and figures.
3. **CERN-OHL-W-2.0 for the RTL**: a license designed for hardware and gateware, with weak reciprocity: anyone who modifies our modules and distributes them must publish the changes. It is more defensive, but it falls outside the licenses recommended by the specification and discourages reuse in corporate contexts.

## Decision

Apache-2.0 for all the code and CC BY 4.0 for documentation, figures, and reports.

## Rationale

The NOTICE file carries the authors' names into every redistribution, even a modified one: it is the strongest attribution among permissive licenses. The patent clause gives a sturdier framework than MIT at no cost to us. CERN-OHL's reciprocity does not serve a project whose purpose is to be read and reused.

## Consequences

- Every source file carries the two SPDX lines (see `CONVENTIONS.md`, Licenses section).
- Third-party material keeps its own license and is listed in `NOTICE`.
- The code stays reusable even in closed products, as long as attribution is kept: this is an accepted consequence.
- Licenses do not protect ideas, only the code and the text. Authorship is documented by the Git history.
