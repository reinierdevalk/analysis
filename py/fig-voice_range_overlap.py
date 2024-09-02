import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
 
title = 'Voice range overlap (mapped ground truth)'
parts = ['M/C', 'C/T', 'T/B']
x_axis_label = 'Piece'
y_axis_label = 'Overlap (%)'
y_ticks = [0, 20, 40, 60, 80, 100]

# input data (output from java code)
pieces = ['AGH','AAD','ACW','BIC','IAW','OLB','OTW','QMS','RUT','SD','TLI','TMI','WP','avg']
MC_vals = [68.42,59.09,60.00,61.11,75.00,55.55,44.44,65.00,50.00,50.00,34.78,50.00,45.00,55.26]
CT_vals = [65.00,75.00,50.00,61.11,72.22,72.22,65.00,56.52,56.52,58.82,55.00,59.09,100.0,65.11]
TB_vals = [43.47,65.21,40.00,34.78,42.85,42.85,68.18,59.09,43.47,30.00,52.38,56.52,27.27,46.62]

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
plt.ylim((y_ticks[0],y_ticks[-1]))

# create bars layout 
full_bar_width = 0.2
bar_width = 0.15

# create plot
plt.bar(pos-(1*full_bar_width),MC_vals,bar_width,color='red',alpha=0.75)
plt.bar(pos+(0*full_bar_width),CT_vals,bar_width,color='blue',alpha=0.75)
plt.bar(pos+(1*full_bar_width),TB_vals,bar_width,color='cyan',alpha=0.75)

plt.legend(parts,bbox_to_anchor=(1.04,0.5), loc='center left')
plt.subplots_adjust(right=0.8) # so that legend does not fall outside
plt.show()