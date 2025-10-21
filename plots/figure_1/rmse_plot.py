import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
matplotlib.rcParams["figure.dpi"] = 300

COLOR = 'red'
def poly_test(x,y):
    degrees,metrics = [],[]
    for degree in range(1,11):
        poly_eq = np.poly1d(np.polyfit(x,y,degree))
        y_pred = poly_eq(x)
        rmse = np.sqrt(mean_squared_error(y,y_pred))
        degrees.append(degree)
        metrics.append(rmse)
    plt.plot(degrees,metrics,color=COLOR)
    plt.scatter(degrees,metrics,s=20,color=COLOR)
    plt.xticks(range(1,11))
    plt.xlim((0,11))
    plt.ylim((2,9))
    plt.xlabel('Polynomial Degree',fontsize=13)
    plt.ylabel('RMSE / GPa',fontsize=13)
    plt.title('RMSE vs Polynomial Degree of fitted Model',fontsize=14)
    plt.savefig('./figure_1.png')
    return (degree,metrics)

x,y = [],[]
with open('./data/exp.txt') as f:
    for line in f.readlines():
        tokens = line.strip().split(',')
        x.append(float(tokens[0]))
        y.append(float(tokens[1]))

degree,metrics = poly_test(x,y)
delta = [metrics[i-1]-metrics[i] for i in range(1,len(metrics))]
print(f'average RMSE improvement after deg 2: {sum(delta[:1])/(len(delta)-1)}')