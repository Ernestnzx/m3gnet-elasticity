# Q-D Structure Computation for M3GNet

This directory contains the scripts needed to run the computation of the Young's moduli using M3GNet machine learning interatomic potential using the modified MD simulation routine as described in the paper. This directory is for computing the total of 100 structures of varying Q-D ratio.

The file structures of `./scripts/inputs` and `./scripts/outputs` to ensure the smooth generation of the input and output files are as follows:
```
./inputs
.
├── annealed
├── deformation
├── melted
└── unmelted
```
```
./outputs
├── annealed_traj
├── log_files
│   ├── annealed
│   ├── deformation
│   ├── melted
│   └── unmelted
├── melted_traj
└── unmelted_traj
```

To run the LAMMPS script, enter the `./scripts` directory and run `bash ./scripts/<script name>` to run an instance of LAMMPS. The input file will be generated and structures will be saved after each phase of the MD.