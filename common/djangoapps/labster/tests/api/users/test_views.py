import json

from django.contrib.auth.models import User

from rest_framework.test import APITestCase


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


class UpdateUserTest(APITestCase):
    pass
