# Initial Setup
- `sudo apt-get update`
- `sudo apt-get upgrade`
- `sudo apt-get install automake build-essential clang cmake git libgmp-dev libntl-dev libsodium-dev libssl-dev libtool python3 python3-pip`
- `pip install scikit-learn pandas fabric`
- `make boost`
- Setup passwordless auth so that it's possible to directly ssh between machines. Refer [https://www.tecmint.com/ssh-passwordless-login-using-ssh-keygen-in-5-easy-steps/](https://www.tecmint.com/ssh-passwordless-login-using-ssh-keygen-in-5-easy-steps/)

Inside the MP-SPDZ directory, run the following:
- `make replicated-ring-party.x` since we use 3 party Replicated Secret Sharing, in the Semi-Honest setting.
- `Scripts/setup-ssl.sh 3` to generate necessary certificates and keys to setup secure channels between parties.
- Edit the HOSTS file with respective username, VM IP address and the output directory.

# Relevant Files
- `Programs/Source/custom_data.mpc`: Returns trained decision tree trained on `x` initialized to a nxm matrix of random values and `y` initialized to a vector of n random values, where n and m are provided as command line arguments. Useful for benchmarking.
- `Programs/Source/breast_tree.mpc`: Returns trained decision tree trained on publicly available breast cancer wisconsin dataset. Useful for accuracy comparison.
- `Compiler/decision_tree_modified.py`: Contains core training protocol based on [https://petsymposium.org/popets/2023/popets-2023-0021.pdf](https://petsymposium.org/popets/2023/popets-2023-0021.pdf).
- `Compiler/decision_tree_new.py`: Contains our optimized training protocol


# Run Baseline
To use a random valued dataset
- Ensure that line 23 of `MP-SPDZ/Programs/Source/custom_data.mpc` is `from Compiler.decision_tree_modified import TreeClassifier`
- Run `Scripts/compile-run.py -H HOSTS -E ring custom_data_dt $((2**13)) 11 4 -Z 3 -R 64` where n = 2^13 , m = 11 and h = 4 in this example

To use the breast cancer wisconsin dataset
- To run implementation baseline ensure that line 25 of `MP-SPDZ/Programs/Source/breast_tree.mpc` is `from Compiler.decision_tree_modified import TreeClassifier`
- `Scripts/compile-run.py -H HOSTS -E ring breast_tree`

# Run Our Protocol

To use a random valued dataset
- Ensure that line 23 of `MP-SPDZ/Programs/Source/custom_data.mpc` is `from Compiler.decision_tree_new import TreeClassifier`
- Run `Scripts/compile-run.py -H HOSTS -E ring custom_data_dt $((2**13)) 11 4 -Z 3 -R 64` where n = 2^13 , m = 11 and h = 4 in this example

To use the breast cancer wisconsin dataset
- To run implementation baseline ensure that line 25 of `MP-SPDZ/Programs/Source/breast_tree.mpc` is `from Compiler.decision_tree_new import TreeClassifier`
- `Scripts/compile-run.py -H HOSTS -E ring breast_tree`
