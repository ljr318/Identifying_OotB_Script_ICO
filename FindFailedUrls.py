import os
import json
path = './ICO_Htmls'
succ_files = os.listdir(path)
failed_files = []
with open('ICO_Website_Urls.json', 'r') as f:
    all_files = json.load(f)
print(len(all_files))
for file in all_files:
    if file["ICO name"] + ".html" not in succ_files:
        failed_files.append(file)
print(len(failed_files))
data_str = json.dumps(failed_files)
with open('ICO_Website_failed_list.json', 'w', encoding='utf-8') as f:
    f.write(data_str)

