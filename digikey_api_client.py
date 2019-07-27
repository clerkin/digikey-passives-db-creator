""" One Class to Rule them all
    Will hold data & behavior: auth info & api methods """

import requests
from requests.exceptions import HTTPError

class ClientAPIError(Exception):
    ''' DigiKey client API error class'''

partsearch_api_url = "https://api.digikey.com/services/partsearch/v2/partdetails"

class DigiKeyAPIClient():
    ''' DK API Client '''

    def __init__(self, client_id, access_token):
        self.client_id = client_id
        self.access_token = access_token

    def search_partdetails(self, MPN):
        """ Returns dict of part details on successful search """
        
        digikey_access_token = self.access_token
        digikey_client_id = self.client_id
    
        api_call_headers = {'authorization': digikey_access_token,
                            'accept': 'application/json',
                            'content-type': 'application/json',
                            'x-ibm-client-id': digikey_client_id}
    
        part_data = {"Part": MPN,
                     "IncludeAllAssociatedProducts":"false",
                     "IncludeAllForUseWithProducts":"false"}

        response_dict = dict()
        try:
            api_call_response = requests.post(partsearch_api_url, 
                                              headers=api_call_headers, 
                                              json=part_data, 
                                              verify=False)
            response_dict = api_call_response.json()
            api_call_response.raise_for_status()
        except HTTPError as http_err:
            if 'The specified part was not found.' in [val for (key, val) in response_dict.items()]:
                raise ClientAPIError('Part not found: {err}'.format(err=response_dict))
            else: 
                raise ClientAPIError('HTTP error occurred: {err}'.format(err=http_err))
        except Exception as err:
            print('Other error occurred: {err}'.format(err=err))
        
        return response_dict


        
        
