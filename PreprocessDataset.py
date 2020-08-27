import os
import json


def del_file(file_path):
    file_list = os.listdir(file_path)
    for file in file_list:
        size = os.path.getsize("./ICO_Sanitized_Htmls/" + file)
        if size < 10 * 1024:
            print("remove", file)
            os.remove("./ICO_Sanitized_Htmls/" + file)

def clean_tech(file_path):
    result_list = []
    with open(file_path) as f:
        data = json.load(f)
    for item in data:
        if len(item['Tech Profile']) >= 5:
            result_list.append(item)
    data_str = json.dumps(result_list, indent=4)
    print(len(result_list))
    with open('SanitizedIcoBackendStackList.json', 'w') as f:
        f.write(data_str)

if __name__ == "__main__":
    file_path = "IcoWebTechProfileList.json"
    clean_tech(file_path)
    dir_path = "./ICO_Sanitized_Htmls"
    del_file(dir_path)


