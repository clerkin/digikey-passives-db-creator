"""Utilies to get and store program configs in JSON format"""

import json

class jsonConfigUtilError(Exception):
    """json config util error class"""

def json_file_to_dict(input_file_name):
    return_dict = {}
    try:
        with open(input_file_name, 'r') as f:
            return_dict = json.load(f)
    except FileNotFoundError as ex:
        raise jsonConfigUtilError("File not found: {0}".format(ex))
    else:
        return return_dict

def dict_to_json_file(dict, output_file_name, indent=4):
    with open(output_file_name, "w") as jsonFile:
        json.dump(dict, jsonFile, indent)