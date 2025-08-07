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
    '333-7-11-18-15-30'  : "07-11-18-15-30",
    '333-9-11-16-15-30'  : "09-11-16-15-30",
    '333-11-11-14-15-30' : "11-11-14-15-30",
    '333-13-11-12-15-30' : "13-11-12-15-30",
    '333-15-11-10-15-30' : "15-11-10-15-30",
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

exp_density, exp_ym = [],[]
with open('./data/exp.txt','r') as f:
    for line in f.readlines():
        tokens = line.split(',')
        exp_density.append(float(tokens[0]))
        exp_ym.append(float(tokens[1]))

# The experimental curve is first fitted first before MSE
# of the different computations are calculated.
exp_density = np.array(exp_density)
exp_ym = np.array(exp_ym)
plt.scatter(exp_density,exp_ym,s=DOT_SIZE,label="Experimental")
poly_f, poly_param = poly_curve(exp_density,exp_ym)
exp_f, exp_param = exp_curve(exp_density,exp_ym)

x_plot = np.linspace(min(exp_density),max(exp_density),200)
y_poly_plot = poly_f(x_plot,*poly_param)
y_exp_plot = exp_f(x_plot,*exp_param)

a1,b1,c1 = poly_param
a2,b2,c2 = exp_param

plt.title(f'Density vs Young Modulus (UFF)',size=title_size)
plt.xlabel('Density / g cm$^{-3}$',size=axis_size)
plt.ylabel("Young Modulus / GPa",size=axis_size)

# Initial point 
df = pd.read_csv('./data/initial_computation.csv')
defect_type = {}
tuple_list = list(sorted(df[['File','Density','E/Gpa']].itertuples(index=False, name=None)))
uff_x,uff_y = [],[]
avg_ym = []
for k,x,y in tuple_list:
    key = labels[re.sub(r'-\d+\.txt$', '', k)]
    if key not in defect_type:
        defect_type[key] = [[],[]]
    defect_type[key][0].append(x)
    defect_type[key][1].append(y)
for k,v in sorted(defect_type.items()):
    x,y = v
    uff_x.extend(x)
    uff_y.extend(y)
    # Change for the number of logfiles computed for each type
    avg_ym.append((k,sum(x)/len(x),sum(y)/len(y)))
    plt.scatter(x,y,s=DOT_SIZE,label=k)

# Computing MSE for the UFF computation.
y_poly_pred = poly_f(np.array(uff_x),*poly_param)
y_exp_pred = exp_f(np.array(uff_x),*exp_param)
rmse_poly = np.sqrt(mean_squared_error(uff_y,y_poly_pred))
rmse_exp = np.sqrt(mean_squared_error(uff_y,y_exp_pred))

poly_label = f'${a1:.1f}x^2{b1:.1f}x+{c1:.1f}$'
exp_label = f'${a2:.1f}e^{{{b2:.1f}x}}+({c2:.1f})$'

plt.plot(x_plot,y_poly_plot,color='red')
plt.plot(x_plot,y_exp_plot,color='purple')
plt.text(0.8125,30.5,f'RMSE (polynomial): {rmse_poly:.3f}\nRMSE (exponential): {rmse_exp:.3f}',fontsize=10)

plt.legend(loc='upper left',prop={"size":11})
plt.xlim(x_axis_range)
plt.ylim(y_axis_range)
plt.savefig('./plots/qd_uff.png')
plt.clf()

plt.title(f'Density vs Young Modulus (UFF)',size=title_size)
plt.xlabel('Density / g cm$^{-3}$',size=axis_size)
plt.ylabel("Young Modulus / GPa",size=axis_size)
plt.xlim(x_axis_range)
plt.ylim(y_axis_range)
plt.plot(x_plot,y_poly_plot,color='red')
plt.plot(x_plot,y_exp_plot,color='purple')
# plt.scatter(exp_density,exp_ym,s=DOT_SIZE,label='Experiments')
for k,v in sorted(defect_type.items()):
    x,y = v
    plt.scatter(x,y,s=DOT_SIZE,alpha=0.1,edgecolors=None)
avg_rmse_x,avg_rmse_y = [],[]
colors = [
    'blue',
    'orange',
    'green',
    'red',
    'purple'
]
for idx,i in enumerate(avg_ym):
    k,x,y = i
    plt.scatter(x,y,s=12,color=colors[idx],label=k)
    avg_rmse_x.append(x)
    avg_rmse_y.append(y)
rmse_poly = np.sqrt(mean_squared_error(avg_rmse_y, poly_f(np.array(avg_rmse_x), *poly_param)))
rmse_exp = np.sqrt(mean_squared_error(avg_rmse_y, exp_f(np.array(avg_rmse_x), *exp_param)))
plt.legend(loc='upper left',prop={"size":11})
plt.text(0.8125,34,f'RMSE (polynomial): {rmse_poly:.3f}\nRMSE (exponential): {rmse_exp:.3f}',fontsize=10)
plt.savefig('./plots/avg_qd_uff.png')
