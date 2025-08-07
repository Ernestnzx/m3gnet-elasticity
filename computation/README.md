# Installing LAMMPS binary

This `README.md` will guide on the user on how to install the LAMMPS with the M3GNet machine learning interatomic potential developed by AdvancedSoft.

1. Add the following lines into your `.bashrc` and activate use the interactive node for installation.
```
shopt -s expand_aliases
alias condaon="conda activate"
alias condaoff="conda deactivate"
alias la="ls -a"
alias lmp="~/lammps/build/lmp_matgl"

module load Miniconda3
module load CUDA/12.4.0
module load CMake/3.27.6-GCCcore-13.2.0
module load OpenMPI/4.1.6-GCC-13.2.0
```
2. Install conda environment using the provided `environment.yml`, without the pip packages and update to `libgcc-ng=13.2.0`.

3. `pip install matgl==1.1.3`

4. `pip uninstall dgl`. This version of DGL does not have CUDA support.

5. `pip install dgl -f https://data.dgl.ai/wheels/torch-2.4/cu124/repo.html`

6. Get modified LAMMPS by cloning the repository [here](https://github.com/advancesoftcorp/lammps/).

7. `cd lammps`, `mkdir build`, `cd build` and type the following compile flags:
```
cmake -C ../cmake/presets/basic.cmake -D BUILD_SHARED_LIBS=on -D LAMMPS_EXCEPTIONS=on -D PKG_PYTHON=on -D PKG_ML-M3GNET=on -D PKG_EXTRA-COMPUTE=on -D PKG_EXTRA-FIX=on -D PKG_MANYBODY=on -D PKG_EXTRA-DUMP=on -D PKG_MOLECULE=on -D Python_EXECUTABLE=<location of your python binary> -D PKG_GPU=on -D GPU_API=cuda -D GPU_PREC=single -D GPU_ARCH=sm_80 -D LAMMPS_MACHINE=matgl -D BUILD_MPI=yes -D CUDA_MPS_SUPPORT=yes ../cmake
```

8. `cmake --build .`

9. `make install`

## Molecular Dynamics calculation of Young's Modulus
- **LAMMPS**: All simulations were run using LAMMPS, a molecular dynamics package.  
  > Thompson, A. P., Aktulga, H. M., Berger, R., Bolintineanu, D. S., Brown, W. M., Crozier, P. S., in ’t Veld, P. J., Kohlmeyer, A., Moore, S. G., Nguyen, T. D., Shan, R., Stevens, M. J., Tranchida, J., Trott, C., & Plimpton, S. J. (2022). *LAMMPS – a flexible simulation tool for particle-based materials modeling at the atomic, meso, and continuum scales*. *Computer Physics Communications, 271*, 108171. https://doi.org/10.1016/j.cpc.2021.108171

- **Example Script**: Elastic tensor calculations are based on the official LAMMPS `ELASTIC` example script located in the [`examples/ELASTIC`](https://github.com/lammps/lammps/tree/develop/examples/ELASTIC_T/DEFORMATION/Silicon) directory of the LAMMPS. The workflow and methodology follow the "Calculate elastic constants" How‑to guide in the LAMMPS documentation [here](https://docs.lammps.org/Howto_elastic.html).
