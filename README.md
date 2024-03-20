Protocols folder contain the single column more detailed version of algorithms. These are just for more information.
Sections folder contains preliminary section, tree training section and correctness proof section which are called in main.tex
To compile (on linux terminal) run pdflatex -> bibtex -> pdflatex. 


Initial Setup
- Build MP-SPDZ from source (TODO: Add more detailed instructions)
- `make replicated-ring-party.x`
- `Scripts/setup-ssl.sh 3`


Run DT Training Protocol
- `Scripts/compile-run.py -H HOSTS -E ring custom_data_dt $((2**13)) 11 4 -Z 3 -R 64`
- `Scripts/compile-run.py -H HOSTS -E ring breast_tree`

