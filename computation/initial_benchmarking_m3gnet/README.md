# Initial Benchmarking

This directory contains the scripts needed to run the computation of the Young's moduli using M3GNet machine learning interatomic potential using the full molecular dynamics (MD) simulation routine as described in the paper.

The file structures of `./inputs` and `./outputs` to ensure the smooth generation of the input and output files are as follows:
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