import matplotlib.pyplot as plt
import palettable
import seaborn as sns
import json
from matplotlib.colors import LinearSegmentedColormap


my_colormap = LinearSegmentedColormap.from_list("", ["white", "blue"])
with open('similarity_matrix.json', 'r') as f:
    data = json.load(f)
#plt.figure(figsize=(10, 10))
sns.heatmap(data=data, vmin=30, vmax=100, cmap=my_colormap)
plt.show()