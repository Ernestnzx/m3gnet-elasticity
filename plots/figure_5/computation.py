import os
import numpy as np
import re

def voigt(c):
    k = (c[0][0] + c[1][1] + c[2][2] + 2*(c[0][1] + c[0][2] + c[1][2]))/9
    g = (c[0][0] + c[1][1] + c[2][2] - (c[0][1] + c[0][2] + c[1][2]) + 3*(c[3][3] + c[4][4] + c[5][5])) / 15
    return (9*k*g)/(3*k+g)

def reuss(s):
    k = 1/((s[0][0] + s[1][1] + s[2][2]) + 2*(s[0][1] + s[1][2] + s[2][0]))
    g = 15/(4*(s[0][0] + s[1][1] + s[2][2]) - 4*(s[0][1] + s[1][2] + s[2][0]) + 3*(s[3][3] + s[4][4] + s[5][5]))
    return (9*k*g)/(3*k+g)

file_path = "./deformation/" # The log files can be generated via computation of structures.
file_paths = [os.path.join(file_path, file) for file in os.listdir(file_path)]
a,b,files = [],[],[]
for file in sorted(file_paths):
    # File exists now lets compute young's modulus
    with open(file, 'r') as f:
        lines = f.readlines()
        c = [[0 for _ in range(6)] for _ in range(6)]
        density = []
        for line in lines:
            line = [word for word in line.split() if word]
            if line and len(line) == 8:
                try: density.append(float(line[-1]))
                except: pass
            if (not line or line[0] != 'Elastic'): continue
            i, j, cij = int(line[2]) - 1, int(line[3]) - 1, float(line[5])
            c[i][j] = c[j][i] = cij

        c = np.array(c)      # Elastic Matrix
        try: s = np.linalg.inv(c) # Compliance Matrix
        except: print(f'unable to compute for {file}')
        density = [i for i in density if 0.5 <= i <= 3.0]
        if not density: continue
        print(f'{os.path.basename(file):<40} {young_modulus:6.3f} {sum(density)/len(density) if density else 0:7.3f}')
        young_modulus = voigt(c)
        np.set_printoptions(precision=3)
        a.append(round(sum(density)/len(density),3))
        b.append(round(young_modulus,3))
        pattern = r'deformation_333[-U]*-?([A-Z0-9]+)'
        files.append(re.match(pattern, file.split('/')[-1]).group(1))

for x,y,f in zip(a,b,files): print(f'{x},{y},{f}')
