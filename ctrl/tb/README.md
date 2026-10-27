# ctrl/tb

One subfolder per testbench: `ctrl/tb/<module>/` with `Makefile` and `test_<module>.py`.
`make test` from the root runs every subfolder containing a Makefile and checks `results.xml`.

Note: with cocotb 2.x some Makefile variables were renamed compared to 1.x.
Check the documentation for the version pinned in `requirements.txt` to see which ones to use.
