""" Tests for digikey_api_client """

import pytest
import responses
from digikey_api_client import ClientAPIError, DigiKeyAPIClient
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

partsearch_api_url = "https://api.digikey.com/services/partsearch/v2/partdetails"

@pytest.fixture
def good_secrets_dict():
    good_secrets_dict = { "client_id": "Meryl",
                          "client_secret": "BigLittleLies",
                          "access_token": "token",
                          "refresh_token": "refresh",
                          "expires_at": "2019-01-01 10:10:10"}
    return good_secrets_dict

# Mock out requests.post to return a 400 error
@responses.activate
def test_client_api_search_partdetail_part_not_found(good_secrets_dict):
    ''' Client should return ClientAPIError when part cannot be found '''
    response_dict = {'Details': 'The specified part FOOBAR was not found',
                     'Message': 'The specified part was not found.',
                     'HttpStatusCode': 400}
    responses.add(responses.POST, 
                  partsearch_api_url,
                  status=400, 
                  json=response_dict)

    dk_api_client = DigiKeyAPIClient(good_secrets_dict['client_id'], 
                                     good_secrets_dict['access_token'])

    with pytest.raises(ClientAPIError):
        dk_api_client.search_partdetails("FOOBAR")
