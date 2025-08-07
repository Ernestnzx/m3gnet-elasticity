#!/bin/bash
#PBS -N lammps_amorphous6
#PBS -l select=1:ngpus=1:mem=30gb
#PBS -l walltime=1:00:00
#PBS -j oe

cd $PBS_O_WORKDIR;

conda activate m3gnet

shopt -s expand_aliases
alias lmp="~/lammps/build/lmp_matgl"
alias run_lammps="lmp -sf gpu -pk gpu 1 -in"

export OMP_NUM_THREADS=1
bash ./routine.sh 333-EXP-11-vasp 300
