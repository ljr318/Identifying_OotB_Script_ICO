import json
import os
import matplotlib.pyplot as plt
import numpy as np
import random
import palettable
import seaborn as sns

ico_list = os.listdir('ICO_Sanitized_Htmls')

with open('similarity_matrix.json', 'r') as f:
    similarity_matrix = json.load(f)

with open('IcoDataList.json', 'r') as f:
    rate_list = json.load(f)

dic = {}
for ico_rate in rate_list:
    dic[ico_rate['ICO name']] = ico_rate['ICO score']

result_list = []
for i, ico in enumerate(ico_list):
    ico_name = ico.replace('.html', '')
    max_similarity = 0
    for j in range(len(ico_list)):
        if j != i:
            max_similarity = max(similarity_matrix[i][j], max_similarity)
    rate = float(dic[ico_name])
    result = list()
    result.append(max_similarity)
    result.append(float(rate))
    result_list.append(result)
data_str = json.dumps(result_list)
with open('correlation_scatter_data.json', 'w') as f:
    f.write(data_str)
print(result_list)
a = np.array(result_list)

# calculate Pearson coefficient
print(np.corrcoef(a[:, 0], a[:, 1]))

# draw scatter diagram
plt.scatter(x=a[:, 0], y=a[:, 1], s=3)
plt.show()
