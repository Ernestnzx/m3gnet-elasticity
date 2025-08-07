# Simplex Relaxation

This directory contains the scripts needed to run the computation of the Young's moduli using M3GNet machine learning interatomic potential at T = 300 K using minimization of the structure as described in the paper.

The file structures of `./inputs` and `./outputs` to ensure the smooth generation of the input and output files are as follows:
```
./inputs
└── deformation
```
```
./outputs
└── log_files
    └── deformation
```

To run the LAMMPS script, enter the `./scripts` directory and run `bash ./scripts/<script name>` to run an instance of LAMMPS. The input file will be generated and structures will be saved after each phase of the MD.