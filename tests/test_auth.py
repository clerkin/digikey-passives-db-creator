from unittest.mock import patch, call
from datetime import datetime
import pytest
from auth import get_auth_code, gen_access_token, get_access_token, \
                 calc_token_expiration_datetime

# Get auth code tests

@pytest.fixture
def empty_dict():
    empty_dict = { "client_id": None,
                   "client_secret": None}
    return empty_dict

def test_get_auth_code_bad_input_type():
    """function expects dict containing client_id & cliend_secret"""
    with pytest.raises(TypeError):
        get_auth_code(list())

def test_get_auth_code_no_id(empty_dict):
    """get auth needs client id to exist in secrets.json"""
    with pytest.raises(ValueError):
        get_auth_code(empty_dict)

@patch('builtins.input', return_value=None)
def test_get_auth_code_no_code_input(input_mock):
    '''Test that user actually input code'''
    secrets_dict = { "client_id": "Meryl",
                     "client_secret": "BigLittleLies"}
    with pytest.raises(ValueError):
        get_auth_code(secrets_dict)


# Generate access token unit tests

def test_gen_access_token_bad_input_type():
    '''get access toekn expects dict input'''
    with pytest.raises(TypeError):
        gen_access_token(list(), "test_auth_code")

def test_gen_access_token_no_secret(empty_dict):
    '''get auth needs client id to exist in secrets.json'''
    with pytest.raises(ValueError):
        gen_access_token(empty_dict, "test_auth_code")


# Get access token tests

def mocked_get_now():
    return datetime(2019, 1, 1, 10, 10, 10)

@patch('auth.get_now', side_effect=mocked_get_now)
def test_get_access_token_valid_token(mock_datetime):
    ''' fn returns secret.json token when within
         valid time'''
    valid_secrets_dict = { "client_id": "Meryl",
                           "client_secret": "BigLittleLies",
                           "access_token": "token",
                           "refresh_token": "refresh",
                           "expires_at": "2019-01-01 11:10:10"}

    access_token = get_access_token(valid_secrets_dict)
    assert access_token == "token"

@patch('auth.get_now', side_effect=mocked_get_now)
@patch('auth.get_auth_code', return_value="code")
@patch('auth.gen_access_token', return_value=None)
def test_get_access_token_invalid_token(mock_datetime, mock_get_auth_code, mock_gen_access_token):
    ''' fn runs get_auth & gen_token when presented
        with invalid time (token is expired)'''
    
    invalid_secrets_dict = { "client_id": "Meryl",
                             "client_secret": "BigLittleLies",
                             "access_token": "token",
                             "refresh_token": "refresh",
                             "expires_at": "2019-01-01 09:10:10"}

    get_access_token(invalid_secrets_dict)
    assert mock_get_auth_code.call_count == 1
    assert mock_gen_access_token.call_count == 1
    
    # check that get_auth & gen_token are called each once


# Calc Token expiration tests
 
def test_calc_token_expiration_non_whole_num_input():
    '''fn should only taken in whole number'''
    with pytest.raises(ValueError):
        calc_token_expiration_datetime(-1)

def test_calc_token_expiration_string_input():
    '''fn should take in var of type int'''
    with pytest.raises(TypeError):
        calc_token_expiration_datetime("86400")

@patch('auth.get_now', side_effect=mocked_get_now)
def test_calc_token_expiration(mock_datetime):
    '''calc's expiration date for UTC time'''

    expected_datetime = datetime(2019, 1, 2, 10, 10, 10)
    expires_in_sec = 86400

    expiration_datetime = calc_token_expiration_datetime(expires_in_sec)
    assert expiration_datetime == expected_datetime
