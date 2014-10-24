import hashlib
import json
import os

import requests

from django.conf import settings


ENDPOINT_DISCOVER_URL = 'http://api.nutshell.com/v1/json'
API_KEY = getattr(settings, 'NUTSHELL_API_KEY')
USERNAME = getattr(settings, 'NUTSHELL_USERNAME')


class Nutshell:

    def __init__(self, username, api_key):
        endpoint = self._get_api_endpoint_for_user(username)
        auth_header = "{}:{}".format(username, api_key)
        auth_header = auth_header.encode('base64').strip()

        self.endpoint = endpoint
        self.auth_header = auth_header

    def call(self, method, params):
        payload = {
            'method': method,
            'params': params,
            'id': self._generate_request_id(),
        }

        payload = json.dumps(payload)
        headers = {
            'Authorization': 'Basic {}'.format(self.auth_header),
        }
        response = requests.post(self.endpoint, payload, headers=headers)
        print method, response.json()['result']['id']
        return response.json()['result']

    def _get_api_endpoint_for_user(self, username):
        payload = {
            'method': 'getApiForUsername',
            'params': {'username': username},
            'id': self._generate_request_id()
        }
        payload = json.dumps(payload)

        response = requests.post(ENDPOINT_DISCOVER_URL, payload)
        assert response.status_code == 200, "invalid response: {}".format(response.status_code)

        output = response.json()
        endpoint = "https://{}/api/v1/json".format(output['result']['api'])
        return endpoint

    def _generate_request_id(self):
        return hashlib.md5(os.urandom(8)).hexdigest()[:8]

    def new_contact(self, name, phone, email):
        params = {
            'contact': {
                'name': name,
                'phone': [phone],
                'email': [email]
            }
        }
        return nutshell.call('newContact', params)

    def new_account(self, contact_id, name):
        params = {
            'account': {
                'name': name,
                'contacts': [
                    {'id': contact_id},
                ]
            }
        }
        return nutshell.call('newAccount', params)

    def new_lead(self, contact_id, account_id):
        params = {
            'lead': {
                'primaryAccount': {'id': account_id},
                'contacts': [
                    {'id': contact_id},
                ]
            }
        }
        return nutshell.call('newLead', params)


def demo():
    nutshell = Nutshell(USERNAME, API_KEY)
    contact = nutshell.new_contact('Tony Stark', '123-456-7890', 'kriwil+ironman@gmail.com')
    account = nutshell.new_account(contact['id'], 'The Avengers')
    lead = nutshell.new_lead(contact['id'], account['id'])
