import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score,mean_squared_error

matplotlib.rcParams["figure.dpi"] = 300
title_size,axis_size = 16,14
data = [
    ('ml','MD simulation using M3GNet'),
    ('vasp','VASP computation'),
    ('forcite','DFT Optimization + COMPASSII FF Computation'),
    ('uff', 'DFT Optimization + UFF Computation'),
]
labels = {
    "EXP" : "07-26-18-00-30",
    "RV"  : "07-11-18-15-30",
    "HD"  : "34-19-10-03-15",
    "50C" : "10-33-20-03-15"
}
DOT_SIZE = 10

def poly_test(x,y):
    best_degree,best_mse,best_pred = -1,np.inf,None
    for degree in range(1,3):
        poly_eq = np.poly1d(np.polyfit(x,y,degree))
        y_pred = poly_eq(x)
        mse = mean_squared_error(y,y_pred)
        if mse >= best_mse: continue
        best_degree = degree
        best_mse = mse
        best_pred = poly_eq
    return (best_degree,best_mse,best_pred)

def poly_curve(x,y):
    f = lambda x,a,b,c : a*x**2+b*x+c
    params,_ = curve_fit(f,x,y)
    y_pred = f(x,*params)
    print(f'Polynomial fit RMSE = {np.sqrt(mean_squared_error(y,y_pred)):.3f} r2 = {r2_score(y,y_pred):.3f}')
    x_plot = np.linspace(min(x),max(x),100)
    y_plot = f(x_plot,*params)
    a,b,c = params
    return (f,params)

def exp_curve(x,y):
    f = lambda x,a,b,c: a*np.exp(b*x)+c
    params,_ = curve_fit(f,x,y)
    y_pred = f(x,*params)
    print(f'Exponential fit RMSE = {np.sqrt(mean_squared_error(y,y_pred)):.3f}, r2 = {r2_score(y,y_pred):.3f}')
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

for filename,label in data:
    comp_x, comp_y = [], []
    with open(f'./data/{filename}.txt','r') as f:
        plt.scatter(exp_density,exp_ym,label='Experiments',s=DOT_SIZE)
        defects = {}
        for line in f.readlines():
            tokens = line.strip().split(',')
            if tokens[-1] not in labels: continue
            defect_type = labels[tokens[-1]]
            if defect_type not in defects:
                defects[defect_type] = [[],[]]
            defects[defect_type][0].append(float(tokens[0]))
            defects[defect_type][1].append(float(tokens[1]))
        for k,v in sorted(defects.items()):
            if k == 'BV' or k == 'S': continue
            x,y = v
            comp_x.extend(x)
            comp_y.extend(y)
            plt.scatter(x,y,s=DOT_SIZE,label=k)

    y_poly_pred = poly_f(np.array(comp_x),*poly_param)
    y_exp_pred = exp_f(np.array(comp_x),*exp_param)

    rmse_poly = np.sqrt(mean_squared_error(comp_y,y_poly_pred))
    rmse_exp = np.sqrt(mean_squared_error(comp_y,y_exp_pred))

    x_plot = np.linspace(min(exp_density),max(exp_density),200)
    y_poly_plot = poly_f(x_plot,*poly_param)
    y_exp_plot = exp_f(x_plot,*exp_param)

    a1,b1,c1 = poly_param
    a2,b2,c2 = exp_param

    poly_label = f'${a1:.1f}x^2{b1:.1f}x+{c1:.1f}$'
    exp_label = f'${a2:.1f}e^{{{b2:.1f}x}}+({c2:.1f})$'

    plt.plot(x_plot,y_poly_plot,color='red')
    plt.plot(x_plot,y_exp_plot,color='purple')
    plt.text(0.825,57,f'RMSE (polynomial): {rmse_poly:.3f}\nRMSE (exponential): {rmse_exp:.3f}',fontsize=10)

    plt.legend(prop={'size':11})
    plt.title(f'Density vs Young Modulus',size=title_size)
    plt.xlabel('Density / g cm$^{-3}$',size=axis_size)
    plt.ylabel("Young Modulus / GPa",size=axis_size)
    plt.xlim((0.8,2.4))
    plt.ylim((0,100))
    plt.savefig(f'./plots/{filename}.png')
    plt.clf()
