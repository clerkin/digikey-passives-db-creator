"""oauth2.0 for DigiKey API"""

"""
    TODO: fix secrets.json sotrage format for datetime remove uS
    TODO: Fix indentation of storing secrets.json
    TODO: Add better error catching for secrets.json (dont write broken json if fails) 
    MISC: Determine better soln for time zone of expiration time """

import requests, json
import datetime
from helpers.json_config_utils import dict_to_json_file

authorize_url = "https://sso.digikey.com/as/authorization.oauth2"
token_url = "https://sso.digikey.com/as/token.oauth2"

#callback url specified when the application was defined
default_callback_uri = "https://localhost"

def get_auth_code(secrets_dict, callback_uri=default_callback_uri):

    validate_client_secrets_dict(secrets_dict)
    client_id = secrets_dict["client_id"]

    authorization_code = None

    while authorization_code is None:
        authorization_redirect_url = authorize_url + '?response_type=code&client_id=' + client_id + '&redirect_uri=' + callback_uri + '&scope=openid'
        print("go to the following url on the browser and enter the code from the returned url: ")
        print("---  " + authorization_redirect_url + "  ---")
        authorization_code = input('code: ')
        if authorization_code is None:
            raise ValueError("No code was entered!")

    return authorization_code

def gen_access_token(secrets_dict, auth_code, callback_uri=default_callback_uri):
    """Get access token from digikey api"""
    if auth_code is None:
        raise ValueError("auth_code cannot be None!")
    
    validate_client_secrets_dict(secrets_dict)
    client_id = secrets_dict["client_id"]   
    client_secret = secrets_dict["client_secret"]

    data = {'grant_type': 'authorization_code', 
            'code': auth_code,     
            'redirect_uri': callback_uri}
    print("requesting access token")
    try:
        access_token_response = requests.post(token_url, 
                                              data=data, 
                                              verify=False, 
                                              allow_redirects=False, 
                                              auth=(client_id, client_secret))
    except Exception as ex:
        raise ex

    tokens = json.loads(access_token_response.text)
    access_token = tokens['access_token']
    refresh_token = tokens['refresh_token']
    expires_in = tokens['expires_in']

    expires_at_datetime = calc_token_expiration_datetime(expires_in)

    secrets_dict['access_token'] = access_token
    secrets_dict['refresh_token'] = refresh_token
    secrets_dict['expires_at'] = datetime_to_str(expires_at_datetime)

    dict_to_json_file(secrets_dict, "secrets.json")


def get_access_token(secrets_dict):
    ''' Get DigiKey API access token
        First checks if valid token exists in secrets.json
        if not, generates new access token '''

    validate_client_secrets_dict(secrets_dict)
    
    # Check if access code in secrets_dict from json has is valid
    if not (secrets_dict['access_token'] is None):
        datetime_now = get_now()
        token_expiration_at_str = secrets_dict['expires_at']
        token_expiration_datetime = str_to_datetime(token_expiration_at_str)

        # if token has not expired, return it
        if datetime_now < token_expiration_datetime:
            return secrets_dict['access_token']

    # generate token if none in secrets_dict or 
    # if token has expired
    auth_code = get_auth_code(secrets_dict)
    gen_access_token(secrets_dict, auth_code)
    return secrets_dict['access_token']

# get now function to enable easier testing
# mocking auth.datetime.datetime preventing
# for now() was perventing other uses of
# datetime methods
def get_now():
    ''' Returns current datetime UTC'''
    return datetime.datetime.now()

def str_to_datetime(str):
    ''' Fn returns datetime object from datetime string
        stored in secrets.json
        datetime string format "%Y-%m-%d %H:%M:%S" '''
    return datetime.datetime.strptime(str, "%Y-%m-%d %H:%M:%S")

def datetime_to_str(dt):
    if isinstance(dt, datetime.datetime):
        return dt.strftime(dt, "%Y-%m-%d %H:%M:%S")
    
def validate_client_secrets_dict(secrets_dict):
    '''Validate that serects dict is in fact a dict and has
       values for client information'''
    if not isinstance(secrets_dict, dict):
        raise TypeError("Input to get auth code should be dict")

    if (secrets_dict["client_secret"] is None):    
        raise ValueError("No client secret present in secrets.jon")
    elif (secrets_dict["client_id"] is None):
        raise ValueError("No client ID present in secrets.jon")

def calc_token_expiration_datetime(expires_in):
    ''' fn to calc at what date time will aquired api
        access token will expire'''
    if not isinstance(expires_in, int):
        raise TypeError("Input to calc_token_expiration_time should be of type int")
    if expires_in <= 0:
        raise ValueError("expires_in time should be > 0")

    datetime_now = get_now()
    expiration_datetime = datetime_now + datetime.timedelta(seconds=expires_in)
    return expiration_datetime

def digikey_secrets_converter(obj):
    if isinstance(obj, datetime.datetime):
        return obj.__str__()

    

# Fn to check if valid access code already exists