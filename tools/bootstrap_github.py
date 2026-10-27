#!/usr/bin/env python3
"""Crea su GitHub label, milestone e issue a partire da docs/requirements.yaml.

Fa il passo 1 del § 8.2 del capitolato: una issue per milestone e una per ogni
requisito (di default solo i MUST). Usa la CLI `gh`, gia' autenticata, e va
lanciato dalla radice di un clone della repository.

Di default NON scrive nulla: stampa i comandi che eseguirebbe. Per eseguirli
davvero aggiungere --apply. Rilanciarlo e' sicuro: salta cio' che esiste gia'.

Esempi:
    python tools/bootstrap_github.py --start 2026-11-02
    python tools/bootstrap_github.py --start 2026-11-02 --apply
    python tools/bootstrap_github.py --start 2026-11-02 --apply --prio MUST SHOULD
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
REQ_FILE = ROOT / "docs" / "requirements.yaml"

AREAS = {
    "PLT": ("area:plant", "Plant HIL su PYNQ-Z1"),
    "CTL": ("area:ctrl", "Controllore su iCE40UP5K"),
    "IF": ("area:if", "Interfacce"),
    "PRF": ("area:prf", "Prestazioni"),
    "VER": ("area:ver", "Verifica e qualita'"),
    "DOC": ("area:doc", "Documentazione"),
}

LABELS = {
    "prio:MUST": ("b60205", "Requisito obbligatorio"),
    "prio:SHOULD": ("d93f0b", "Requisito atteso"),
    "prio:COULD": ("c5def5", "Requisito facoltativo"),
    "owner:A": ("0e8a16", "Responsabile A (analogico/potenza)"),
    "owner:D": ("1d76db", "Responsabile D (digitale/FPGA)"),
    "owner:A+D": ("5319e7", "Responsabilita' condivisa"),
    "type:requirement": ("ededed", "Issue generata da un requisito"),
    "type:milestone": ("fbca04", "Criteri di uscita di una milestone"),
    **{label: ("bfdadc", desc) for label, desc in AREAS.values()},
}

# Criteri di uscita delle milestone (tabella 7.2), in forma di checklist.
EXIT_CRITERIA = {
    "M0": [
        "Toolchain installate e versioni scritte in tools/versions",
        "Repository con struttura e CI verde su un modulo d'esempio",
        "Un LED lampeggia su entrambe le schede",
        "Cavi verificati con test di continuita' e loopback",
        "D0 completato",
    ],
    "M1": [
        "Modelli Python medio, commutato e di piccolo segnale, con test",
        "Grandezze derivate del § 3.5 e budget",
        "D1 in bozza",
        "Riesame DR1 (Appendice D.1)",
    ],
    "M2": [
        "ICD congelato (D2)",
        "Link PYNQ-Z1 -> iCE40 funzionante in PRBS",
        "DPWM sull'iCE40 con P1-P6 dimostrate",
        "TC-03, TC-04 e TC-17 superati per la parte disponibile",
    ],
    "M3": [
        "Plant v1 con API, cattura e generatore interno",
        "TC-01 e TC-02 superati",
        "Controllore v1 in co-simulazione con soft-start e gradino (VER-04)",
    ],
    "M4": [
        "Primo anello chiuso sull'hardware",
        "TC-05, TC-06, TC-07, TC-18 al livello MUST",
        "Riesame DR2 (Appendice D.2)",
        "Elenco delle funzionalita' congelato",
    ],
    "M5": [
        "AVP, bilanciamento, protezioni, FRA, Zout, transitori di linea e VID",
        "TC-08 ... TC-16 al livello MUST",
        "SHOULD avviati in ordine di priorita'",
    ],
    "M6": [
        "Campagna di collaudo completa in un'unica sessione",
        "D5 e D6 consegnati",
        "Repository pubblica e release v1.0",
        "Riesame finale DR3 (Appendice D.3)",
    ],
}


def gh(args: list[str], apply: bool, read: bool = False) -> str:
    """Esegue `gh`. Le letture si fanno sempre; le scritture solo con --apply."""
    if not apply and not read:
        print("  [dry-run] gh " + " ".join(_quote(a) for a in args))
        return ""
    res = subprocess.run(["gh", *args], text=True, capture_output=True)
    if res.returncode != 0:
        sys.exit(f"gh {' '.join(args)}\n{res.stderr.strip()}")
    return res.stdout


def _quote(s: str) -> str:
    return s if s and all(c.isalnum() or c in "-_:/.=+" for c in s) else repr(s)


def due_date(start: dt.date, week: int) -> str:
    """Fine della settimana `week` (domenica), formato richiesto dall'API."""
    day = start + dt.timedelta(days=7 * week - 1)
    return f"{day.isoformat()}T23:59:59Z"


def requirement_body(r: dict) -> str:
    area = AREAS[r["id"].split("-")[0]][1]
    verify = ", ".join(str(v) for v in r["verify"])
    return (
        f"**{r['id']}** · {r['prio']} · {area}\n\n"
        f"{r['title']}.\n\n"
        f"Testo vincolante: capitolato VRM4-HIL v1.0, § 4.\n\n"
        f"| Campo | Valore |\n|---|---|\n"
        f"| Verifica | {verify} |\n"
        f"| Milestone | {r['ms']} |\n"
        f"| Responsabile (proposta) | {r['owner']} |\n\n"
        f"### Fatto quando\n"
        f"- [ ] Implementato e passato in revisione (PR collegata)\n"
        f"- [ ] Verifica ({verify}) eseguita\n"
        f"- [ ] Evidenza archiviata (file di risultati in `reports/` o riferimento al report)\n"
    )


def milestone_body(key: str) -> str:
    items = "\n".join(f"- [ ] {c}" for c in EXIT_CRITERIA[key])
    return (
        "Criteri di uscita (capitolato, tabella 7.2). La milestone e' raggiunta "
        "quando sono tutti spuntati, non quando scade la settimana.\n\n" + items + "\n"
    )


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--start", required=True, type=dt.date.fromisoformat,
                   help="lunedi' della settimana 1 (AAAA-MM-GG)")
    p.add_argument("--prio", nargs="+", default=["MUST"], choices=["MUST", "SHOULD", "COULD"],
                   help="priorita' per cui creare issue (default: MUST)")
    p.add_argument("--apply", action="store_true", help="esegue davvero (default: dry-run)")
    a = p.parse_args()

    if a.start.weekday() != 0:
        sys.exit(f"--start {a.start} non e' un lunedi'")

    data = yaml.safe_load(REQ_FILE.read_text(encoding="utf-8"))
    milestones: dict = data["milestones"]
    reqs = [r for r in data["requirements"] if r["prio"] in a.prio]

    # Stato attuale della repository (letture: si fanno anche in dry-run).
    existing_ms = set()
    existing_issues = set()
    if a.apply:
        existing_ms = {m["title"] for m in json.loads(
            gh(["api", "repos/{owner}/{repo}/milestones?state=all&per_page=100"], a.apply, read=True))}
        existing_issues = {i["title"] for i in json.loads(
            gh(["issue", "list", "--state", "all", "--limit", "1000", "--json", "title"], a.apply, read=True))}

    print("== Label")
    for name, (color, desc) in LABELS.items():
        gh(["label", "create", name, "--color", color, "--description", desc, "--force"], a.apply)

    print("== Milestone")
    for key, m in milestones.items():
        if m["title"] in existing_ms:
            print(f"  esiste gia': {m['title']}")
            continue
        gh(["api", "repos/{owner}/{repo}/milestones", "-f", f"title={m['title']}",
            "-f", f"due_on={due_date(a.start, m['week'])}",
            "-f", f"description=Fine settimana {m['week']}"], a.apply)

    print("== Issue delle milestone")
    for key, m in milestones.items():
        title = f"{m['title']}: criteri di uscita"
        if title in existing_issues:
            print(f"  esiste gia': {title}")
            continue
        gh(["issue", "create", "--title", title, "--body", milestone_body(key),
            "--label", "type:milestone", "--milestone", m["title"]], a.apply)

    print(f"== Issue dei requisiti ({', '.join(a.prio)}: {len(reqs)})")
    for r in reqs:
        title = f"{r['id']}: {r['title']}"
        if title in existing_issues:
            print(f"  esiste gia': {title}")
            continue
        labels = ["type:requirement", f"prio:{r['prio']}", AREAS[r["id"].split("-")[0]][0], f"owner:{r['owner']}"]
        args = ["issue", "create", "--title", title, "--body", requirement_body(r),
                "--milestone", milestones[r["ms"]]["title"]]
        for lab in labels:
            args += ["--label", lab]
        gh(args, a.apply)

    if not a.apply:
        print("\nDry-run: nulla e' stato scritto. Rilanciare con --apply per eseguire.")


if __name__ == "__main__":
    main()
