import os
import sys
import matplotlib.pyplot as plt
import numpy as np

def voigt_scheme(c):
    k = (c[0][0] + c[1][1] + c[2][2] + 2*(c[0][1] + c[0][2] + c[1][2])) / 9
    g = (c[0][0] + c[1][1] + c[2][2] - (c[0][1] + c[0][2] + c[1][2]) + 3*(c[3][3] + c[4][4] + c[5][5])) / 15
    return (9*k*g)/(3*k+g)

filename = sys.argv[1]
with open(f'./output/log.{filename}','r') as f:
    c = [[0 for _ in range(6)] for _ in range(6)]
    density = 0
    for line in f.readlines():
        line = [word for word in line.split()]
        if line and line[0] == "density": density = float(line[-1])
        if not line or line[0] != "Elastic": continue
        i,j,cij = int(line[2])-1,int(line[3])-1,float(line[5])
        c[i][j] = c[j][i] = cij
    c = np.array(c)
    try: s = np.linalg.inv(c)
    except: 
        print(f"Unable to invert matrix for {filename}")

open('./data.txt','a').write(f"{filename},{voigt_scheme(c)},{density}\n")

