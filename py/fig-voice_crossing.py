import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
 
title = 'Voice crossing (mapped ground truth)'
parts = ['Medius', 'Contratenor', 'Tenor', 'Bassus', 'avg'] 
x_axis_label = 'Piece'
y_axis_label = 'Notes involved (%)'
y_ticks = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]

# input data (output from java code)
pieces = ['AGH','AAD','ACW','BIC','IAW','OLB','OTW','QMS','RUT','SD','TLI','TMI','WP','avg']
medius_vals = [05.83, 08.21, 01.16, 09.23, 04.30, 02.66, 05.35, 07.10, 03.96, 04.65, 02.56, 02.85, 03.06, 04.69]
contra_vals = [10.85, 23.19, 13.69, 16.66, 17.30, 13.74, 17.00, 16.99, 06.89, 15.66, 07.31, 07.95, 32.55, 15.37]
tenor_vals = [06.48, 15.50, 11.84, 07.93, 16.83, 11.42, 13.72, 12.08, 03.42, 11.84, 04.00, 07.77, 30.76, 11.81]
bassus_vals = [00.00, 02.06, 00.00, 00.00, 02.22, 01.48, 02.43, 02.75, 00.48, 00.00, 00.00, 02.59, 00.00, 01.08]
avg_vals = [05.79, 12.24, 06.67, 08.45, 10.16, 07.32, 09.63, 09.73, 03.69, 08.03, 03.47, 05.29, 16.59, 08.24]

# create general layout
sns.set(style='white')
plt.title(title,fontsize=18)
ax = plt.gca()
ax.grid(which='major', axis='y', linestyle=':')
for spine in ax.spines.values():
    spine.set_edgecolor('lightgray')

# create axis layout
plt.xlabel(x_axis_label, fontsize=16)
pos = np.arange(len(pieces))
plt.xticks(pos, pieces)
plt.ylabel(y_axis_label, fontsize=16)
ax.set_yticks(y_ticks, minor=False)
plt.ylim((y_ticks[0], y_ticks[-1]))

# create bars layout 
full_bar_width = 0.2
bar_width = 0.15

# create plot
plt.bar(pos-(2*full_bar_width),medius_vals,bar_width,color='red',alpha=0.75)
plt.bar(pos-(1*full_bar_width),contra_vals,bar_width,color='blue',alpha=0.75)
plt.bar(pos+(0*full_bar_width),tenor_vals,bar_width,color='cyan',alpha=0.75)
plt.bar(pos+(1*full_bar_width),bassus_vals,bar_width,color='green',alpha=0.75)
plt.bar(pos+(2*full_bar_width),avg_vals,bar_width,color='magenta',alpha=0.75)

plt.legend(parts,bbox_to_anchor=(1.04,0.5), loc='center left')
plt.subplots_adjust(right=0.8) # so that legend does not fall outside
plt.show()