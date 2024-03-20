N_values=($((2**13)) $((2**18)) $((2**19)) $((2**13)) $((2**13)) $((2**13)) $((2**13)) $((2**13)) $((2**13)))
m_values=(11 11 11 20 50 100 11 11 11)
h_values=(4 4 4 4 4 4 10 20 50)

if test -f temp_outputs.txt; then
	rm temp_outputs.txt
fi
for ((i=0; i<${#N_values[@]}; i++)); do
        N="${N_values[i]}"
        m="${m_values[i]}"
        h="${h_values[i]}"
        compile_run_args="-H HOSTS -E ring custom_data_dt $N $m $h -Z 3 -R 64"
	echo "N: $N" >> temp_outputs.txt
	echo "m: $m" >> temp_outputs.txt
	echo "h: $h" >> temp_outputs.txt
        echo >> temp_outputs.txt
	Scripts/compile-run.py $compile_run_args &>> temp_outputs.txt
        echo >> temp_outputs.txt
done
