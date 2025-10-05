# Q-D Structure Computation for UFF

This directory contains the scripts needed to run the computation of the Young's moduli using the Universal Forcefield potential and modified MD simulation routine as described in the paper. This directory is for computing the total of 100 structures of varying Q-D ratio.

Here is the file structure to ensure the smooth generation of the input and output files:
```
└── qd_uff_static
    ├── cif
    ├── computation.py
    ├── dat
    ├── input
    ├── output
    ├── routine.sh
    └── uff_generator.sh
```
To run the LAMMPS script, run `bash ./routine.sh` to generate the structures for relaxation and computation.
