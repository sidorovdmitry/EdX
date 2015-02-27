import json

import requests

from django.conf import settings

from labster.user_utils import get_names


CONSUMER_KEY = settings.SF_CONSUMER_KEY
CONSUMER_SECRET = settings.SF_CONSUMER_SECRET
CALLBACK_URL = settings.SF_CALLBACK_URL
SECURITY_TOKEN = settings.SF_SECURITY_TOKEN
USERNAME = settings.SF_USERNAME
PASSWORD = settings.SF_PASSWORD
INSTANCE_URL = settings.SF_INSTANCE_URL
API_VERSION = settings.SF_API_VERSION

LOGIN_URL = 'https://login.salesforce.com/services/oauth2/token'
LIST_OBJECTS_URL = '{instance_url}/services/data/{api_version}/sobjects/'
OBJECT_URL = '{instance_url}/services/data/{api_version}/sobjects/{object_name}/'
DESCRIBE_URL = '{instance_url}/services/data/{api_version}/sobjects/{object_name}/describe'
QUERY_URL = '{instance_url}/services/data/{api_version}/query/'


def login():
    payload = {
        'grant_type': 'password',
        'client_id': CONSUMER_KEY,
        'client_secret': CONSUMER_SECRET,
        'username': USERNAME,
        'password': '{}{}'.format(PASSWORD, SECURITY_TOKEN),
    }

    response = requests.post(LOGIN_URL, data=payload)
    assert response.status_code == 200, response.content
    content = json.loads(response.content)
    return content['access_token']


def list_accounts():
    headers = {'Authorization': "Bearer {}".format(login())}

    url = QUERY_URL.format(
        instance_url=INSTANCE_URL, api_version=API_VERSION,
    )

    payload = {
        'q': "SELECT Id, Name FROM Account",
    }

    response = requests.get(url, params=payload, headers=headers)
    assert response.status_code == 200, response.content
    content = json.loads(response.content)
    results = []
    # return content['totalSize'], content['done']
    for record in content['records']:
        results.append((record['Id'], record['Name']))

    return results


def create_account(name):
    headers = {
        'Authorization': "Bearer {}".format(login()),
        'Content-Type': "application/json",
    }
    url = OBJECT_URL.format(
        instance_url=INSTANCE_URL, api_version=API_VERSION,
        object_name='Account')

    payload = {
        'Name': name,
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    assert response.status_code == 201, response.content
    content = json.loads(response.content)
    return content['id']


def create_lead(name, email, company, phone, occupation):
    headers = {
        'Authorization': "Bearer {}".format(login()),
        'Content-Type': "application/json",
    }
    url = OBJECT_URL.format(
        instance_url=INSTANCE_URL, api_version=API_VERSION,
        object_name='Lead')

    first_name, last_name = get_names(name)

    payload = {
        'FirstName': first_name,
        'LastName': last_name,
        'Email': email,
        'Company': company,
        'Title': occupation,
        'Phone': phone,
        'LeadSource': 'Web',
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    assert response.status_code == 201, response.content
    content = json.loads(response.content)
    return content['id']
