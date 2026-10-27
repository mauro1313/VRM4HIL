# ctrl/tb

Una sottocartella per banco: `ctrl/tb/<modulo>/` con `Makefile` e `test_<modulo>.py`.
`make test` dalla radice esegue ogni sottocartella che contiene un Makefile e controlla `results.xml`.

Nota: con cocotb 2.x alcune variabili del Makefile hanno cambiato nome rispetto alla 1.x.
Controllate sulla documentazione della versione fissata in `requirements.txt` quali usare.
