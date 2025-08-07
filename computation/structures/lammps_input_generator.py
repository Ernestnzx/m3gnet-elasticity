import os
import warnings
from pymatgen.core import Structure
from pymatgen.io.lammps.data import LammpsData
warnings.simplefilter("ignore")

# Converting from cif files to poscars to .dat files for lammps
for filename in sorted(list(os.listdir('./cif/'))):
    name = filename.split('.')[0]
    print(f"Converting cif to LAMMPS dat file for {name}")
    structure = Structure.from_file(f'./cif/{filename}')
    LammpsData.from_structure(structure, atom_style='atomic').write_file(f'./dat/{name}.dat')