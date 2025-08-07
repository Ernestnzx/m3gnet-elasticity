
#!/bin/bash
#PBS -N type2-14
#PBS -l select=1:ngpus=1:mem=50gb
#PBS -l walltime=09:00:00
#PBS -j oe

cd $PBS_O_WORKDIR;

conda activate m3gnet

shopt -s expand_aliases
alias lmp="~/lammps/build/lmp_matgl"
alias run_lammps="lmp -sf gpu -pk gpu 1 -in"

export OMP_NUM_THREADS=1
bash ./routine.sh 333-9-11-16-15-30-14 300
