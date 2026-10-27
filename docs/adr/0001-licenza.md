# 0001. Licenze del progetto

- Stato: proposta
- Data: 2026-10-27
- Autori: A, D
- Requisiti: § 1.5 (proprietà intellettuale), § 7.9 criterio 5

## Contesto

Il capitolato chiede una repository pubblica con licenza open source a scelta, con Apache-2.0 o MIT consigliate. La repository contiene codice (RTL Verilog per iCE40 e Zynq, Python, script di build) e documentazione (deliverable D0–D6, figure, report). Non contiene progetti di circuiti stampati: le schede sono commerciali.

Il progetto è dimostrativo, ma vogliamo che chi lo riusa ne citi gli autori e che resti chiaro quali parti sono nostre.

## Alternative considerate

1. **MIT per tutto**: testo brevissimo, massima diffusione. Chiede solo di conservare l'avviso di copyright. Non dice nulla su brevetti e modifiche e non distingue codice e testi.
2. **Apache-2.0 per il codice, CC BY 4.0 per la documentazione**: permissiva come la MIT. In più ha l'obbligo di conservare il file NOTICE e di segnalare i file modificati, una concessione esplicita sui brevetti e l'esclusione dei marchi. CC BY è la licenza di riferimento per testi e figure.
3. **CERN-OHL-W-2.0 per l'RTL**: licenza nata per hardware e gateware, con reciprocità debole: chi modifica i nostri moduli e li distribuisce deve pubblicare le modifiche. È più difensiva, ma esce dalle licenze consigliate dal capitolato e scoraggia il riuso in contesti aziendali.

## Decisione

Apache-2.0 per tutto il codice e CC BY 4.0 per documentazione, figure e report.

## Motivazione

Il NOTICE porta i nomi degli autori in ogni ridistribuzione, anche modificata: è l'attribuzione più forte fra le licenze permissive. La clausola sui brevetti dà una cornice più solida della MIT a costo zero per noi. La reciprocità della CERN-OHL non serve a un progetto il cui scopo è essere letto e riusato.

## Conseguenze

- Ogni file sorgente porta le due righe SPDX (vedere `CONVENTIONS.md`, sezione Licenze).
- Il materiale di terzi conserva la propria licenza ed è elencato in `NOTICE`.
- Il codice resta riusabile anche in prodotti chiusi, purché con attribuzione: è una conseguenza accettata.
- Le licenze non proteggono le idee, solo il codice e i testi. La paternità è documentata dalla cronologia Git.
