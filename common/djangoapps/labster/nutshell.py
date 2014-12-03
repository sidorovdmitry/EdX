import hashlib
import json
import os

import requests

from django.conf import settings
from labster.models import NutshellUser


ENDPOINT_DISCOVER_URL = 'http://api.nutshell.com/v1/json'
API_KEY = getattr(settings, 'NUTSHELL_API_KEY')
USERNAME = getattr(settings, 'NUTSHELL_USERNAME')
TAG = 'EdX'
SOURCE_ID = 11
PLAY_LAB_ACTIVITY_ID = 47
VIEW_COURSE_ACTIVITY_ID = 43
INVITE_STUDENTS_ACTIVITY_ID = 51


def get_lead_id(user):
    try:
        obj = NutshellUser.objects.get(user=user)
    except NutshellUser.DoesNotExist:
        return None

    return obj.lead_id


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

    def new_contact(self, name, email, phone):
        params = {
            'contact': {
                'name': name,
                'email': [email],
                'tags': [TAG],
            }
        }

        if phone:
            params['contact'].update({
                'phone': [phone],
            })
        return self.call('newContact', params)

    def new_account(self, contact_id, name):
        params = {
            'account': {
                'name': name,
                'contacts': [
                    {'id': contact_id},
                ],
                'tags': [TAG],
            }
        }
        return self.call('newAccount', params)

    def new_lead(self, contact_id, account_id=None):
        params = {
            'lead': {
                # 'primaryAccount': {'id': account_id},
                'contacts': [
                    {'id': contact_id},
                ],
                'sources': [
                    {'id': SOURCE_ID},
                ],
                'tags': [TAG],
            }
        }

        if account_id:
            params['lead']['primaryAccount'] = account_id

        return self.call('newLead', params)

    def new_activity(self, lead_id, activity_id, name, description):
        now = timezone.now()
        now_iso = now.isoformat()
        params = {
            'activity': {
                'name': name,
                'description': description,
                'activityTypeId': activity_id,
                'startTime': now_iso,
                'endTime': now_iso,
                'leads': [
                    {
                        'entityType': "Leads",
                        'id': lead_id,
                    },
                ],
                'isAllDay': False,
                'isTimed': False,
                'isFlagged': False,
                'status': 1,
            }
        }

        self.call('newActivity', params)

    def play_lab(self, lead_id, user_name, lab_name):
        name = "Play {}".format(lab_name)
        description = "{} plays {}".format(user_name, lab_name)
        self.new_activity(lead_id, PLAY_LAB_ACTIVITY_ID, name, description)

    def view_course(self, lead_id, user_name, course_name):
        name = "View {}".format(course_name)
        description = "{} views {}".format(user_name, course_name)
        self.new_activity(lead_id, VIEW_COURSE_ACTIVITY_ID, name, description)


    def invite_students(self, lead_id, user_name, course_id):
        name = "Invite Students to {}".format(course_id)
        description = "{} invites students to {}".format(user_name, course_id)
        self.new_activity(lead_id, INVITE_STUDENTS_ACTIVITY_ID, name, description)


def create_new_lead(name, email, phone=''):
    """
    return contact, lead
    """
    nutshell = Nutshell(USERNAME, API_KEY)
    contact = nutshell.new_contact(name, email, phone)
    # account = nutshell.new_account(contact['id'], name)
    lead = nutshell.new_lead(contact['id'])
    return (contact['id'], lead['id'])


def play_lab(user, lab):
    nutshell = Nutshell(USERNAME, API_KEY)
    lead_id = get_lead_id(user)
    if not lead_id:
        return

    nutshell.play_lab(lead_id, user.profile.name, lab.name)


def view_course(user, course_name):
    nutshell = Nutshell(USERNAME, API_KEY)
    lead_id = get_lead_id(user)
    if not lead_id:
        return

    nutshell.view_course(lead_id, user.profile.name, course_name)


def invite_students(user, course_id):
    nutshell = Nutshell(USERNAME, API_KEY)
    lead_id = get_lead_id(user)
    if not lead_id:
        return

    nutshell.invite_students(lead_id, user.profile.name, course_id)


def demo():
    nutshell = Nutshell(USERNAME, API_KEY)
    contact = nutshell.new_contact('Tony Stark', '123-456-7890', 'kriwil+ironman@gmail.com')
    account = nutshell.new_account(contact['id'], 'The Avengers')
    lead = nutshell.new_lead(contact['id'], account['id'])
