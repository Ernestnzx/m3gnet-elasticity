import os

defects = [
    ('type1','7-11-18-15-30'),
    ('type2','9-11-16-15-30'),
    ('type3','11-11-14-15-30'),
    ('type4','13-11-12-15-30'),
    ('type5','15-11-10-15-30'),
]
dat_file_path = '../dat/'
for defect, composition in defects:
    if os.path.isdir(f'./{defect}'):
        for file in os.listdir(f'./{defect}'):
            file_path = os.path.join(f'./{defect}', file)
            if os.path.isfile(file_path):
                os.remove(file_path)
    for i in range(1,21):
        filename = f'333-{composition}-{i}'
        filepath = f'{dat_file_path}{filename}.dat'
        if not os.path.exists(filepath): continue
        print(f'Generating script for 333-{composition}-{i}')
        scriptpath = f'./{defect}/{defect}-{i:02}.sh'
        script = f"""
#!/bin/bash
#PBS -N {defect}-{i:02}
#PBS -l select=1:ngpus=1:mem=50gb
#PBS -l walltime=09:00:00
#PBS -j oe

cd $PBS_O_WORKDIR;

conda activate m3gnet

shopt -s expand_aliases
alias lmp="~/lammps/build/lmp_matgl"
alias run_lammps="lmp -sf gpu -pk gpu 1 -in"

export OMP_NUM_THREADS=1
bash ./routine.sh {filename} 300
"""
        with open(scriptpath, 'w') as f:
            f.write(script)
