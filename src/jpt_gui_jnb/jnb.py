import json
import os
import random
from functools import reduce

import time

import sklearn.datasets
from jpt_gui_jnb import jnb
import os
import jpt

import jpt_gui


def app_path_str(book_path_str: str, options: str = ""):
    ready_options = options
    app_path = []
    modul_path = jpt_gui.__file__.split(os.sep)
    modul_path[-1] = "app.py" # change the __init__.py to app.py
    book_path = book_path_str.split(os.sep)
    for i in range(1, len(book_path)-1):
        if book_path[-i] in modul_path:
            [app_path.append("..") for x in range(1, i)]
            match_string = book_path[-i]
            is_after_match: bool = False
            for folder in modul_path:
                if is_after_match:
                    app_path.append(folder)
                elif match_string == folder:
                    is_after_match = True
            break

    app_path_str = reduce(lambda x, y: x + y + "/", app_path, "")
    app_path_str = app_path_str[0:-1]

    json_begin = -1
    json_end = -1
    if "-t" in options or "--tree" in options:
        in_json = False
        for i in range(0, len(options)-1):
            if not in_json and (options[i:i+2] == "-t" or options[i:i+6] == "--tree"):
                in_json = True
                for j in range(i, len(options)-1):
                    if options[j] == '{':
                        json_begin = j
                        break
                if json_begin == -1:
                    raise Exception("Not Correct JSON/Tree Structure")
                break
        json_end = len(options) - 1
        for k in range(len(options)-1, json_begin, -1):
            if options[k:k+1] in ['-f', '-h', '-p', '-j'] or options[k:k+6] in ["--file", "--host", "--port", "--help"] or options[k:k+9] in ["--jupyter"]:
                for s in range(k, max(0, k-10), -1): #if there is the Bracket it should be in prev. 10 Charackters
                    if options[s] == "}":
                        json_end = s +1
                        break
        if json_end == len(options)-1:
            for z in range(len(options)-1, json_begin, -1):
                if options[z] == '}':
                    json_end = z +1
                    break

        tree_str = options[json_begin:json_end]
        file_path = book_path_str + f"/temp_tree_{int(time.time_ns())}.jpt"
        while os.path.exists(file_path):
            file_path += str(random.randint(0,9))

        with open(file_path, "w") as file:
            file.write(tree_str)
            file.close()


        ready_options = options[:json_begin] + file_path + options[json_end:]
    return app_path_str + " " + ready_options

def app_path(book_path_str: str, options: dict = {}):

    app_path = []
    modul_path = jpt_gui.__file__.split(os.sep)
    modul_path[-1] = "app.py" # change the __init__.py to app.py
    book_path = book_path_str.split(os.sep)
    for i in range(1, len(book_path)-1):
        if book_path[-i] in modul_path:
            [app_path.append("..") for x in range(1, i)]
            match_string = book_path[-i]
            is_after_match: bool = False
            for folder in modul_path:
                if is_after_match:
                    app_path.append(folder)
                elif match_string == folder:
                    is_after_match = True
            break

    app_path_str = reduce(lambda x, y: x + y + "/", app_path, "")
    app_path_str = app_path_str[0:-1]

    if '-t' in options.keys() or '--tree' in options.keys():
        symbol = '-t' if '-t' in options.keys() else '--tree'
        tree_str = options.get(symbol).to_json().__str__()
        file_path = book_path_str + f"/temp_tree_{int(time.time_ns())}.jpt"
        while os.path.exists(file_path):
            file_path += str(random.randint(0,9))

        with open(file_path, "w") as file:
            file.write(tree_str)
            file.close()
        options.update({symbol: file_path})

    options_str = " "
    for k, v in options.items():
        options_str += f" {k} {v}"
    return app_path_str + options_str



# Define a custom JSON decoder

class CustomDecoder(json.JSONDecoder):
    def decode(self, s):
        # Swap quotes for valid JSON snytax
        s = s.replace("'", "\"")
        # Replace "inf" with "null" in the JSON string before parsing
        s = s.replace('None', 'null').replace('inf', '"inf"')
        # Use the default JSON decoder to parse the modified string
        parsed = super().decode(s)
        # Replace any "null" values with positive infinity
        return self.replace_inf(parsed)

    def replace_inf(self, obj):
        if isinstance(obj, dict):
            return {key: self.replace_inf(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self.replace_inf(item) for item in obj]
        elif obj == '"inf"':
            return float('inf')
        return obj

if __name__ == '__main__':
    data = sklearn.datasets.load_breast_cancer(as_frame=True)

    df = data.data
    target = data.target
    target[target == 1] = "malignant"
    target[target == 0] = "friendly"

    df["malignant"] = target

    variables = jpt.variables.infer_from_dataframe(df)

    model = jpt.trees.JPT(variables, min_samples_leaf=1 / 569)

    model.fit(df)
    print("start")
    data = {'-t': model}

    t= app_path(os.getcwd(), data)

    print(t)
    # addr = '/home/mrskooma/PyProjects/jpt-gui/exampels'
        # op = "-t {'variables': [{'name': 'Baum', 'domain': {'type': 'numeric', 'class': 'Numeric'}, 'settings': {'min_impurity_improvement': 0, 'blur': 0, 'max_std_lbl': 0.0, 'precision': 0.01}, 'type': 'numeric'}], 'targets': ['Baum'], 'features': ['Baum'], 'min_samples_leaf': 1, 'min_impurity_improvement': 0, 'max_leaves': None, 'max_depth': inf, 'minimal_distances': {}, 'dependencies': {'Baum': ['Baum']}, 'leaves': [], 'innernodes': [], 'priors': {}, 'root': None} -p 8051"
        # t = app_path(addr)
        # print(t)
        # # to_json = "{'variables': [{'name': 'Baum', 'domain': {'type': 'numeric', 'class': 'Numeric'}, 'settings': {'min_impurity_improvement': 0, 'blur': 0, 'max_std_lbl': 0.0, 'precision': 0.01}, 'type': 'numeric'}], 'targets': ['Baum'], 'features': ['Baum'], 'min_samples_leaf': 1, 'min_impurity_improvement': 0, 'max_leaves': None, 'max_depth': inf, 'minimal_distances': {}, 'dependencies': {'Baum': ['Baum']}, 'leaves': [], 'innernodes': [], 'priors': {}, 'root': None}"
        # # to_json_e = '{"variables": [{"name": "Baum", "domain": {"type": "numeric", "class": "Numeric"}, "settings": {"min_impurity_improvement": 0, "blur": 0, "max_std_lbl": 0.0, "precision": 0.01}, "type": "numeric"}], "targets": ["Baum"], "features": ["Baum"], "min_samples_leaf": 1, "min_impurity_improvement": 0, "max_leaves": None, "max_depth": inf, "minimal_distances": {}, "dependencies": {"Baum": ["Baum"]}, "leaves": [], "innernodes": [], "priors": {}, "root": None}'
        # # to_json_r = to_json.replace("\'", "\#").replace('\"', '\'').replace("\#", "\"")
        # # try:
        # #     j = json.loads(to_json.replace("None", "null"), cls=CustomDecoder)
        # #     print(type(j))
        # # except json.decoder.JSONDecodeError as e:
        # #     # Print the error message and the problematic part of the JSON string
        # #     print(f"JSONDecodeError: {e}")
        # #     print(f"Problematic JSON substring: {to_json[max(0, e.pos): e.pos+30]}")




    # if "-t" in options or "--tree" in options:
    #     brackets_depth = 0
    #     in_json = False
    #     for i in range(0, len(options)-1):
    #         if not in_json and (options[i:i+2] == "-t" or options[i:i+6] == "--tree"):
    #             in_json = True
    #             for j in range(i, len(options)-1):
    #                 if options[j] == '{':
    #                     json_begin = j
    #                     break
    #             if json_begin == -1:
    #                 raise Exception("Not Correct JSON/Tree Structure")
    #             continue
    #         if i > json_begin-1:
    #             if options[i] == '{':
    #                 brackets_depth += 1
    #             elif options[i] == '}':
    #                 brackets_depth -= 1
    #             if brackets_depth == 0:
    #                 json_end = i+1
    #                 break
    #             elif brackets_depth < 0:
    #                 raise Exception("not Correct JSON/Tree Structure")