#!/bin/bash
OMP_NUM_THREADS=12
alias lmp="~/lammps/build/lmp"
for file in ./cif/*; do
    filename="$(basename "$file" .cif)"
    if ! [[ -f "./output/log.${filename}" ]]; then
        bash ./uff_generator.sh ${filename}
        lmp -in ./input/in.${filename}
        rm log.lammps restart_${filename}.equil
        python3 ./computation.py ${filename}
    else
        echo "${filename} has been computed, skipping simulation..."
    fi
done

