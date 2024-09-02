import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
 
title = 'Voice range (mapped ground truth)'
parts = ['Medius', 'Contratenor', 'Tenor', 'Bassus']
x_axis_label = 'Piece'
y_axis_label = 'Pitch'
y_ticks = [31, 43, 55, 67, 79]
y_labels = ['G$_1$', 'G$_2$', 'G$_3$', 'G$_4$', 'G$_5$']

# input data (output from java code)
pieces = ['AGH','AAD','ACW','BIC','IAW','OLB','OTW','QMS','RUT','SD','TLI','TMI','WP','avg']
medius_vals = [[54, 72],[57, 74],[55, 74],[55, 70],[53, 72],[58, 70],[60, 72],[55, 69],[60, 74],[58, 70],[60, 75],[60, 72],[61, 74],[57, 72]]
contra_vals = [[55, 67],[53, 69],[56, 67],[53, 65],[53, 67],[53, 67],[55, 67],[50, 67],[53, 70],[51, 67],[53, 67],[53, 69],[55, 69],[53, 68]]
tenor_vals = [[48, 67],[50, 67],[50, 64],[48, 63],[50, 65],[50, 65],[48, 67],[45, 62],[48, 65],[53, 62],[48, 63],[48, 65],[55, 69],[49, 65]]
bassus_vals = [[45, 57],[45, 64],[45, 57],[41, 55],[45, 58],[45, 58],[46, 62],[41, 57],[43, 57],[43, 58],[43, 58],[43, 60],[48, 60],[44, 59]]

# create general layout 
sns.set(style='white')
plt.figure(figsize=(10,3))
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
ax.set_yticklabels(y_labels)
plt.ylim((y_ticks[0],y_ticks[-1]))

# create bars layout 
full_bar_width = 0.2
bar_width = 0.15

# create bars
all_vals = [medius_vals, contra_vals, tenor_vals, bassus_vals]
all_lower = []
all_upper = []
for i in range(0, len(all_vals)):
	curr_vals = all_vals[i]
	all_lower.append([curr_vals[j][0] for j in range(0, len(curr_vals))])
	all_upper.append([curr_vals[j][1] - curr_vals[j][0] for j in range(0, len(curr_vals))])
medius_lower, contra_lower, tenor_lower, bassus_lower = [item for item in all_lower]
medius_upper, contra_upper, tenor_upper, bassus_upper = [item for item in all_upper]

# create plot
plt.bar(pos-(1.5*full_bar_width),medius_lower,bar_width,color='white',alpha=0, label='_nolegend_')
plt.bar(pos-(1.5*full_bar_width),medius_upper,bar_width,color='red',alpha=0.75,bottom=medius_lower)
plt.bar(pos-(0.5*full_bar_width),contra_lower,bar_width,color='white',alpha=0, label='_nolegend_')
plt.bar(pos-(0.5*full_bar_width),contra_upper,bar_width,color='blue',alpha=0.75,bottom=contra_lower)
plt.bar(pos+(0.5*full_bar_width),tenor_lower,bar_width,color='white',alpha=0, label='_nolegend_')
plt.bar(pos+(0.5*full_bar_width),tenor_upper,bar_width,color='cyan',alpha=0.75,bottom=tenor_lower)
plt.bar(pos+(1.5*full_bar_width),bassus_lower,bar_width,color='white',alpha=0, label='_nolegend_')
plt.bar(pos+(1.5*full_bar_width),bassus_upper,bar_width,color='green',alpha=0.75,bottom=bassus_lower)

plt.legend(parts,bbox_to_anchor=(1.04,0.5), loc='center left')
plt.subplots_adjust(right=0.8) # so that legend does not fall outside
plt.show()