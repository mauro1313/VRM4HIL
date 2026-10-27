## Cosa cambia e perché

<!-- Una o due frasi. Collegate la issue: "Closes #NN". Requisiti toccati: CTL-xx, PLT-xx... -->

## Come è stato verificato

<!-- Test aggiunti o modificati, comando per rieseguirli, esito. -->

## Checklist (Appendice D.4)

- [ ] Il cambiamento ha un test che fallirebbe senza di esso
- [ ] RTL: reset dei registri che servono, nessun latch inferito
- [ ] RTL: attraversamenti di dominio solo con sincronizzatori o FIFO
- [ ] RTL: larghezze e formati in virgola fissa dichiarati in testa al modulo
- [ ] Nessun nuovo warning del linter
- [ ] Modello bit-true aggiornato nello stesso commit dell'RTL
- [ ] Timing e occupazione non peggiorati oltre la soglia concordata (riepilogo CI)
- [ ] Python: unità nei nomi, niente valori incollati nel codice
- [ ] Documentazione e `docs/icd/regs.yaml` aggiornati se cambia il comportamento visibile
- [ ] Se cambia l'ICD: revisione dell'ICD approvata da A e D
