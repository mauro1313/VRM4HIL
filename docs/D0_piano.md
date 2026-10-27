# D0 — Piano di progetto

Scadenza: fine della settimana 1 (M0). Da compilare insieme, A e D.

## 1. Date

| Voce | Valore |
|---|---|
| Inizio (lunedì della settimana 1) | AAAA-MM-GG |
| Fine (settimana 16) | AAAA-MM-GG |
| Allineamento settimanale | giorno, ora, durata 30 min |
| Revisione delle pull request | entro 48 ore |

Le milestone con le date esatte sono su GitHub (generate da `tools/bootstrap_github.py`).

## 2. Ruoli

| | A | D |
|---|---|---|
| Profilo | analogico/potenza | digitale/FPGA |
| Responsabile di | modelli, budget, controllo, validazione del plant, misure | RTL del controllore, DPWM, link, formale, pipeline del plant, CI |

### Regola di contaminazione (§ 2.4)

| Chi | Modulo RTL non banale di cui è autore | Notebook di modellazione di cui è autore |
|---|---|---|
| A | | |
| D | | |

## 3. WBS raffinata

Partite dalla tabella 7.3 del capitolato e spezzate ogni riga in attività da al più 4 ore,
ognuna con una issue. Qui solo il riepilogo per settimana.

| Sett. | A | D | Insieme |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| ... | | | |

## 4. Calendario personale

Settimane con disponibilità ridotta (ferie, scadenze di lavoro):

| Chi | Settimane | Ore disponibili |
|---|---|---|
| | | |

## 5. Convenzioni

Vedi [`CONVENTIONS.md`](CONVENTIONS.md). Versioni dei tool in [`../tools/versions`](../tools/versions).

## 6. Registro dei rischi

Partite dalla tabella 7.4 del capitolato. Aggiornato a ogni milestone.

| ID | Rischio | P | I | Mitigazione | Resp. | Stato |
|---|---|---|---|---|---|---|
| R1 | Timing del DPWM a ~100 MHz su UP5K | M | A | sonda di timing anticipata; comparatori registrati | D | aperto |
| R2 | Overflow o instabilità numerica del plant | M | A | | A | aperto |
| R3 | Integrità del segnale sul link a 50 MHz | M | M | | D | aperto |
| R4 | Interazioni fra fasi indotte dal campionamento | A | A | | A | aperto |
| R5 | Ritardo complessivo oltre il budget | M | A | | A+D | aperto |
| R6 | Tempo disponibile insufficiente | A | M | | A+D | aperto |
| R7 | Immagine PYNQ e Vivado incompatibili | M | M | overlay banale in M0 | D | aperto |
| R8 | Danni per cablaggio errato | B | A | | A | aperto |
| R9 | Deriva dell'ambito | M | M | | A+D | aperto |
| R10 | Debug difficile sull'iCE40 | A | M | | D | aperto |

## 7. Ordine di riduzione dell'ambito (§ 7.7)

Se a M3 o M4 il ritardo supera una settimana, si rinuncia nell'ordine a:
tutti i COULD; CTL-16 e IF-05; PLT-13; PLT-17; CTL-15; CTL-14. I MUST non si toccano.
