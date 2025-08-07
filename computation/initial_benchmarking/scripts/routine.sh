#!/bin/bash
shopt -s expand_aliases
OMP_NUM_THREADS=1
alias lmp="~/lammps/build/lmp_matgl"
alias run_lammps="lmp -sf gpu -pk gpu 0 -in"

if [[ $# -ne 2 ]]; then
    echo "Usage: ./routine.sh <filename> <temperature>"
    exit 1
fi

# Relaxing the structure at 300K over 100ps using NVT and NPT 
filename=$1
temperature=$2
python3 m3gnet_generator.py ${filename} ${temperature}

if [[ ! -e "../structures/unmelted/unmelted_$filename.restart" ]]; then
    echo $filename' for unmelted relaxtion not found. Running simulation...'
    run_lammps ../inputs/unmelted/input_$filename.lammps
    if [[ $? -ne 0 ]]; then
        echo 'Unmelted relaxation failed. Exiting process...'
        exit 0
    fi
else
    echo $filename' for unmelted relaxation found! Skipping unmelted relaxation...'
fi

# Melting the structure
melted="melted_${filename}_${temperature}.restart"
if [[ ! -e "../structures/melted/${melted}" ]]; then
    echo $filename' for melted structure at '${temperature}'K is not found. Running simulation...'
    run_lammps ../inputs/melted/input_${filename}_${temperature}.lammps
    if [[ $? -ne 0 ]]; then
        echo 'Melting failed. Exiting process...'
        exit 0
    fi
else
    echo $filename' for melted structure at '${temperature}'K found! Skipping melted relaxation...'
fi

# Annealing the structure
annealed="annealed_${filename}_${temperature}.restart"
if [[ ! -e "../structures/annealed/${annealed}" ]]; then
    echo $filename' for annealed structure at '${temperature}'K is not found. Running simulation...'
    run_lammps ../inputs/annealed/input_${filename}_${temperature}.lammps
    if [[ $? -ne 0 ]]; then
        echo 'Annealing failed. Exiting process...'
        exit 0
    fi
else
    echo $filename' for annealed structure at '${temperature}'K found! Skipping melted relaxation...'
fi

# Computationally breaking the material
deformation="deformation_${filename}_${temperature}.log"
if [[ ! -e "../outputs/log_files/deformation/${deformation}" ]]; then
    echo Log file for $filename' deformation after annealing at '${temperature}'K is not found. Running simulation...'
    run_lammps ../inputs/deformation/input_${filename}_${temperature}.lammps
    if [[ $? -ne 0 ]]; then
        echo 'Deformation failed. Exiting process...'
        exit 0
    fi
    rm ./restart_${filename}.equil
else
    echo Computation for $filename done. Terminating program...
fi

rm log.lammps

