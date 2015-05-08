import json
import unittest
from datetime import date

from django.contrib.auth.models import User
from django.conf import settings

from rest_framework.test import APITestCase

from labster.models import LabsterUser
from student.models import UserProfile


@unittest.skipUnless(settings.ROOT_URLCONF == 'lms.urls', 'Test only valid in lms')
class UserCreateTest(APITestCase):

    def setUp(self):
        self.url = '/labster/api/users/'

    def test_get(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, 405)

    def test_post_no_data(self):
        response = self.client.post(self.url, format='json')
        self.assertEqual(response.status_code, 400)

    def test_post_no_email(self):
        data = {'email': ""}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_post(self):
        data = {'email': "user@email.com"}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 201)

        users = User.objects.filter(email=data['email'])
        self.assertTrue(users.exists())

        user = users[0]
        self.assertFalse(user.has_usable_password())

        content = json.loads(response.content)
        self.assertEqual(content['id'], user.id)
        self.assertEqual(content['email'], user.email)
        self.assertEqual(content['token_key'], user.labster_user.token_key)

    def test_post_unusable_password(self):
        data = {'email': "user@email.com"}

        user = User(username='testusername', email=data['email'])
        user.set_unusable_password()
        user.save()

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 201)

        users = User.objects.filter(email=data['email'])
        self.assertTrue(users.exists())
        self.assertEqual(users[0].id, user.id)

        user = users[0]
        self.assertFalse(user.has_usable_password())

        content = json.loads(response.content)
        self.assertEqual(content['id'], user.id)
        self.assertEqual(content['email'], user.email)
        self.assertEqual(content['token_key'], user.labster_user.token_key)


@unittest.skipUnless(settings.ROOT_URLCONF == 'lms.urls', 'Test only valid in lms')
class UserViewTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='username', email='user@email.com', password='password')
        self.url = '/labster/api/users/{}/'.format(self.user.id)

        labster_user = LabsterUser.objects.get(user=self.user)
        labster_user.date_of_birth = date(2000, 1, 1)
        labster_user.language = 'en'
        labster_user.nationality = 'ID'
        labster_user.save()

    def assertLabsterUser(self, old, new):
        fields = ['nationality', 'language', 'date_of_birth', 'unique_id']
        for field in fields:
            self.assertEqual(getattr(old, field), getattr(new, field))

    def test_not_logged_in(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, 401)

        response = self.client.post(self.url, format='json')
        self.assertEqual(response.status_code, 401)

        response = self.client.put(self.url, format='json')
        self.assertEqual(response.status_code, 401)

    def test_get(self):
        self.client.login(username='username', password='password')
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, 200)

        labster_user = LabsterUser.objects.get(user=self.user)
        profile = UserProfile.objects.get(user=self.user)

        content = json.loads(response.content)
        self.assertEqual(content['user_id'], self.user.id)
        self.assertEqual(
            content['date_of_birth'],
            labster_user.date_of_birth.strftime('%Y-%m-%d'))
        self.assertEqual(content['nationality'], labster_user.nationality.code)
        self.assertEqual(content['language'], labster_user.language)
        self.assertEqual(content['unique_id'], labster_user.unique_id)
        self.assertEqual(content['is_labster_verified'], labster_user.is_labster_verified)
        self.assertEqual(content['name'], profile.name)

    def test_put(self):
        self.client.login(username='username', password='password')
        data = {
            'date_of_birth': "2001-01-01",
            'nationality': "US",
            'language': "zh",
            'unique_id': "aabbcc",
            'user_type': 1,
            'phone_number': "123456",
            'user_school_level': 1,
            'gender': "m",
            'year_of_birth': 2000,
            'level_of_education': "hs",
            'organization_name': "Org Name",
        }
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, 200)

        labster_user = LabsterUser.objects.get(user=self.user)
        profile = UserProfile.objects.get(user=self.user)

        self.assertEqual(
            data['date_of_birth'],
            labster_user.date_of_birth.strftime('%Y-%m-%d'))
        self.assertEqual(data['nationality'], labster_user.nationality.code)
        self.assertEqual(data['language'], labster_user.language)
        self.assertEqual(data['phone_number'], labster_user.phone_number)
        self.assertEqual(data['user_school_level'], labster_user.user_school_level)
        self.assertEqual(data['unique_id'], labster_user.unique_id)
        self.assertEqual(data['user_type'], labster_user.user_type)
        self.assertEqual(data['organization_name'], labster_user.organization_name)
        self.assertEqual(data['gender'], profile.gender)
        self.assertEqual(data['year_of_birth'], profile.year_of_birth)
        self.assertEqual(data['level_of_education'], profile.level_of_education)

    def test_put_update_name(self):
        old_labster_user = LabsterUser.objects.get(user=self.user)

        self.client.login(username='username', password='password')
        data = {'name': "The Name"}
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, 200)

        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.name, data['name'])

        new_labster_user = LabsterUser.objects.get(user=self.user)
        self.assertLabsterUser(old_labster_user, new_labster_user)

    def test_put_update_password(self):
        old_labster_user = LabsterUser.objects.get(user=self.user)

        self.client.login(username='username', password='password')
        data = {'password': "The Name"}
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, 200)

        user = User.objects.get(id=self.user.id)
        self.assertTrue(user.check_password(data['password']))

        new_labster_user = LabsterUser.objects.get(user=self.user)
        self.assertLabsterUser(old_labster_user, new_labster_user)
