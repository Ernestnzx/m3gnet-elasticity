import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import re
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score,mean_squared_error

matplotlib.rcParams["figure.dpi"] = 300
DOT_SIZE,title_size,axis_size = 5,16,14
x_axis_range,y_axis_range = (0.8,1.6),(0,60)

labels = {
    "EXP" : "07-26-18-00-30",
    "RV"  : "07-11-18-15-30",
    "HD"  : "34-19-10-03-15",
    "50C" : "10-33-20-03-15"
}

def poly_curve(x,y):
    f = lambda x,a,b,c : a*x**2+b*x+c
    params,_ = curve_fit(f,x,y)
    y_pred = f(x,*params)
    print(f'Polynomial fit MSE = {mean_squared_error(y,y_pred):.3f} r2 = {r2_score(y,y_pred):.3f}')
    x_plot = np.linspace(min(x),max(x),100)
    y_plot = f(x_plot,*params)
    a,b,c = params
    return (f,params)

def exp_curve(x,y):
    f = lambda x,a,b,c: a*np.exp(b*x)+c
    params,_ = curve_fit(f,x,y)
    y_pred = f(x,*params)
    print(f'Exponential fit MSE = {mean_squared_error(y,y_pred):.3f}, r2 = {r2_score(y,y_pred):.3f}')
    x_plot = np.linspace(min(x),max(x),100)
    y_plot = f(x_plot,*params)
    a,b,c = params
    return (f,params)

with open('./data/exp.txt','r') as f:
    exp_density, exp_ym = [],[]
    for line in f.readlines():
        tokens = line.split(',')
        exp_density.append(float(tokens[0]))
        exp_ym.append(float(tokens[1]))

# The experimental curve is first fitted first before MSE
# of the different computations are calculated.
exp_density = np.array(exp_density)
exp_ym = np.array(exp_ym)
poly_f, poly_param = poly_curve(exp_density,exp_ym)
exp_f, exp_param = exp_curve(exp_density,exp_ym)

x_plot = np.linspace(min(exp_density),max(exp_density),200)
y_poly_plot = poly_f(x_plot,*poly_param)
y_exp_plot = exp_f(x_plot,*exp_param)

# Adding the points to the plot
datapoints = {}
plt.scatter(exp_density,exp_ym,s=DOT_SIZE,label="Experimental")
with open('./data/data_with_npt.txt','r') as f:
    for line in f.readlines():
        tokens = line.strip().split(',')
        structure_type = re.match(r"^\d+-(.+)-\d+$",tokens[0]).group(1)
        datapoints.setdefault(structure_type,[]).append((float(tokens[1]),float(tokens[2])))

comp_x,comp_y,avg_density,avg_ym = [],[],[],[]
for k,v in sorted(datapoints.items(),key=lambda x: int(x[0].split('-')[0])):
    ym,density = list(zip(*v))
    comp_x.extend(density)
    comp_y.extend(ym)
    avg_ym.append(sum(ym)/len(ym))
    avg_density.append(sum(density)/len(density))
    plt.scatter(density,ym,s=DOT_SIZE,label=k)

y_poly_pred = poly_f(np.array(comp_x),*poly_param)
y_exp_pred = exp_f(np.array(comp_x),*exp_param)
rmse_poly = np.sqrt(mean_squared_error(comp_y,y_poly_pred))
rmse_exp = np.sqrt(mean_squared_error(comp_y,y_exp_pred))

plt.plot(x_plot,y_poly_plot,color='red')
plt.plot(x_plot,y_exp_plot,color='purple')
plt.title(f'Density vs Young Modulus (UFF)',size=title_size)
plt.xlabel('Density / g cm$^{-3}$',size=axis_size)
plt.ylabel("Young Modulus / GPa",size=axis_size)
plt.xlim(x_axis_range)
plt.ylim(y_axis_range)
plt.text(0.8125,32.5,f'RMSE (polynomial): {rmse_poly:.3f}\nRMSE (exponential): {rmse_exp:.3f}',fontsize=10)
plt.legend()
plt.savefig('./plots/qd_with_npt.png')
plt.clf()

plt.title(f'Density vs Young Modulus (UFF)',size=title_size)
plt.xlabel('Density / g cm$^{-3}$',size=axis_size)
plt.ylabel("Young Modulus / GPa",size=axis_size)
plt.xlim(x_axis_range)
plt.ylim(y_axis_range)
plt.plot(x_plot,y_poly_plot,color='red')
plt.plot(x_plot,y_exp_plot,color='purple')
# plt.scatter(exp_density,exp_ym,s=DOT_SIZE,label='Experiments')
colors = [
    'blue',
    'orange',
    'green',
    'red',
    'purple'
]
for i,(k,v) in enumerate(sorted(datapoints.items(),key=lambda x: int(x[0].split('-')[0]))):
    ym,density = list(zip(*v))
    plt.scatter(density,ym,s=DOT_SIZE,edgecolors=None,alpha=0.1)
    plt.scatter(avg_density[i],avg_ym[i],s=12,color=colors[i],label=k)
plt.legend(loc='upper left',prop={"size":11})
plt.text(0.8125,34,f'RMSE (polynomial): {rmse_poly:.3f}\nRMSE (exponential): {rmse_exp:.3f}',fontsize=10)
plt.savefig('./plots/avg_qd_uff.png')
