import os
import warnings
from pymatgen.core import Structure
from pymatgen.io.lammps.data import LammpsData
warnings.simplefilter("ignore")

script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
skipped_files = []
for root, dirs, files in os.walk(script_dir):
    if 'dat' in root: continue
    for file in files:
        if file.startswith('.') or not file.endswith('.cif'): continue
        filepath = os.path.join(root, file)
        if filepath.endswith('.cif') and os.path.getsize(filepath) < 30 * 1024:
            skipped_files.append(file)
            continue
        name = file.split('.')[0]
        print(f"Converting cif to LAMMPS dat file for {name}")
        structure = Structure.from_file(filepath)
        LammpsData.from_structure(structure, atom_style='atomic').write_file(f'../dat/{name}.dat')
