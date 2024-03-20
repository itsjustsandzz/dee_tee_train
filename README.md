
Initial Setup
- Build MP-SPDZ from source (Section **TL;DR (Source Distribution)** at [https://github.com/data61/MP-SPDZ](https://github.com/data61/MP-SPDZ))
- `make replicated-ring-party.x`
- `Scripts/setup-ssl.sh 3`

Run DT Training Protocol
- `Scripts/compile-run.py -H HOSTS -E ring custom_data_dt $((2**13)) 11 4 -Z 3 -R 64`
    - To run implementation baseline ensure that line 23 of `MP-SPDZ/Programs/Source/custom_data.mpc` is `from Compiler.decision_tree_modified import TreeClassifier`
    - To run our training protocol ensure that line 23 of `MP-SPDZ/Programs/Source/custom_data.mpc` is `from Compiler.decision_tree_new import TreeClassifier`
- `Scripts/compile-run.py -H HOSTS -E ring breast_tree`
    - To run implementation baseline ensure that line 25 of `MP-SPDZ/Programs/Source/breast_tree.mpc` is `from Compiler.decision_tree_modified import TreeClassifier`
    - To run our training protocol ensure that line 25 of `MP-SPDZ/Programs/Source/breast_tree.mpc` is `from Compiler.decision_tree_new import TreeClassifier`
