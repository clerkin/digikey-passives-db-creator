import requests, json
import subprocess
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


authorize_url = "https://sso.digikey.com/as/authorization.oauth2"
token_url = "https://sso.digikey.com/as/token.oauth2"

#callback url specified when the application was defined
callback_uri = "https://localhost"

test_api_url = "https://api.digikey.com/services/partsearch/v2/partdetails"

#client (application) credentials - located at apim.byu.edu
with open('secrets.json', 'r') as json_file:
    secrets_dict = json.load(json_file)

client_id = secrets_dict['client_id']
client_secret = secrets_dict['client_secret']

#step A - simulate a request from a browser on the authorize_url - will return an authorization code after the user is
# prompted for credentials.

authorization_redirect_url = authorize_url + '?response_type=code&client_id=' + client_id + '&redirect_uri=' + callback_uri + '&scope=openid'


print("go to the following url on the browser and enter the code from the returned url: ")
print("---  " + authorization_redirect_url + "  ---")
authorization_code = input('code: ')

# step I, J - turn the authorization code into a access token, etc
data = {'grant_type': 'authorization_code', 
        'code': authorization_code,     
        'redirect_uri': callback_uri}
print("requesting access token")
access_token_response = requests.post(token_url, data=data, verify=False, allow_redirects=False, auth=(client_id, client_secret))

print("response")
print(access_token_response.headers)
print('body: ' + access_token_response.text)

# we can now use the access_token as much as we want to access protected resources.
tokens = json.loads(access_token_response.text)
access_token = tokens['access_token']
print("access token: " + access_token)

api_call_headers = {'authorization': access_token,
                    'accept': 'application/json',
                    'content-type': 'application/json',
                    'x-digikey-customer-id': '8141098',
                    'x-ibm-client-id': client_id}
part_data = {"Part":"2N7002-HF","IncludeAllAssociatedProducts":"false","IncludeAllForUseWithProducts":"false"}
api_call_response = requests.post(test_api_url, headers=api_call_headers, data=part_data, verify=False)

print(api_call_response)