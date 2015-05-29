from django.contrib.auth.models import User
from django.test import TestCase

from labster_lti.utils import get_username, create_user


class GetUsernameTest(TestCase):

    def test_short(self):
        username = get_username('1', 'test')
        self.assertEqual(len(username), 30)

    def test_long(self):
        username = get_username('a1b2c3' * 10, 'test123' * 10)
        self.assertEqual(len(username), 30)


class CreateUserTest(TestCase):

    def test_new(self):
        external_user_id = '123'
        provider = 'test'
        username = get_username(external_user_id, provider)
        user = create_user(external_user_id, provider)

        self.assertEqual(
            user.id,
            User.objects.get(username=username).id
        )

    def test_exist(self):
        external_user_id = '123'
        provider = 'test'
        username = get_username(external_user_id, provider)
        existing_user = User.objects.create_user(
            username=username,
            email='test@email.com',
            password='test')
        user = create_user(external_user_id, provider)

        self.assertEqual(
            user.id,
            existing_user.id,
        )
