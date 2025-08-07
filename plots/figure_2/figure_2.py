import matplotlib
import matplotlib.pyplot as plt
matplotlib.rcParams["figure.dpi"] = 300

timesteps = [0,200000,300000,400000,1100000,1200000]
temperature = [300,300,1000,1000,300,300]

# Create the plot
plt.plot(timesteps, temperature, linestyle='-', color='blue', label='Heating Curve')

# Vertical Dotted lines
plt.axvline(x=100000,  color='black', linestyle='--', linewidth=0.75)
plt.axvline(x=200000,  color='black', linestyle='--', linewidth=0.75)
plt.axvline(x=300000,  color='black', linestyle='--', linewidth=0.75)
plt.axvline(x=400000,  color='black', linestyle='--', linewidth=0.75)
plt.axvline(x=1100000, color='black', linestyle='--', linewidth=0.75)

# Text labels for MD sim pipeline
plt.text(50000,   350, 'NVT', ha='center', fontsize=10, color='black')
plt.text(150000,  350, 'NPT', ha='center', fontsize=10, color='black')
plt.text(250000,  350, 'NVT', ha='center', fontsize=10, color='black') 
plt.text(350000,  350, 'NPT', ha='center', fontsize=10, color='black')
plt.text(800000, 350, 'NPT annealing', ha='center', fontsize=10, color='black')
plt.text(1150000, 350, 'NPT', ha='center', fontsize=10, color='black')

# Add labels, title, and legend
plt.xlabel('Timestep',size=14)
plt.ylabel('Temperature (K)',size=14)
plt.xlim((0,1.2e6))
plt.ylim((200,1100))
plt.title('Temperature vs. Timestep',size=16)
plt.legend()
plt.savefig('./figure_2.png')
