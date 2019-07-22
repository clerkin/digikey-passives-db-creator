"""Test Doc String"""

import pytest
from helpers.json_config_utils import json_file_to_dict, dict_to_json_file, jsonConfigUtilError

def test_json_file_to_dict_invalid_file():
    with pytest.raises(jsonConfigUtilError):
        json_file_to_dict("missing_file.json")

