from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone

from labster_backoffice.models import License
from labster.tests.views import ViewTestMixin
from labster.tests.factories import LicenseFactory, UserFactory


class LicenseListTest(ViewTestMixin, TestCase):

    def setUp(self):
        self.url = reverse('license:index')
        User.objects.create_user('username', 'user@email.com', 'password')


class LicenseCreateTest(ViewTestMixin, TestCase):

    def setUp(self):
        self.url = reverse('license:create')
        User.objects.create_user('username', 'user@email.com', 'password')
        self.date_end = timezone.now()

        self.valid_data = {
            'user': UserFactory().id,
            'item_count': 1,
            'date_bought': self.date_end.strftime('%Y-%m-%d %H:%M'),
            'date_end_license': self.date_end.strftime('%Y-%m-%d %H:%M'),
            'is_active': 1,
        }

    def test_post_valid_data(self):
        self.client.login(username='username', password='password')
        response = self.client.post(self.url, self.valid_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('license:index'))

        license = License.objects.latest('id')
        self.assertEqual(license.user.id, self.valid_data['user'])
        self.assertTrue(license.is_active)
        self.assertEqual(license.item_count, self.valid_data['item_count'])
        self.assertEqual(
            license.date_bought.strftime('%Y-%m-%d %H:%M'),
            self.valid_data['date_bought'])
        self.assertEqual(
            license.date_end_license.strftime('%Y-%m-%d %H:%M'),
            self.valid_data['date_end_license'])


class LicenseUpdateTest(ViewTestMixin, TestCase):

    def setUp(self):
        self.license = LicenseFactory()
        self.url = reverse('license:update', args=[self.license.id])
        User.objects.create_user('username', 'user@email.com', 'password')
        self.date_end = timezone.now()

        self.valid_data = {
            'user': UserFactory().id,
            'item_count': 1,
            'date_bought': self.date_end.strftime('%Y-%m-%d %H:%M'),
            'date_end_license': self.date_end.strftime('%Y-%m-%d %H:%M'),
            'is_active': 1,
        }

    def test_post_valid_data(self):
        self.client.login(username='username', password='password')
        response = self.client.post(self.url, self.valid_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('license:index'))

        license = License.objects.get(id=self.license.id)
        self.assertEqual(license.user.id, self.valid_data['user'])
        self.assertTrue(license.is_active)
        self.assertEqual(license.item_count, self.valid_data['item_count'])
        self.assertEqual(
            license.date_bought.strftime('%Y-%m-%d %H:%M'),
            self.valid_data['date_bought'])
        self.assertEqual(
            license.date_end_license.strftime('%Y-%m-%d %H:%M'),
            self.valid_data['date_end_license'])


class DeactivateLicenseTest(ViewTestMixin, TestCase):

    def setUp(self):
        user = User.objects.create_user('username', 'user@email.com', 'password')
        self.license = LicenseFactory(user=user)
        self.url = reverse('license:deactivate', args=[self.license.id])

    def test_get_logged_in(self):
        self.client.login(username='username', password='password')

        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('license:index'))

        license = License.objects.get(id=self.license.id)
        self.assertFalse(license.is_active)


class ActivateLicenseTest(ViewTestMixin, TestCase):

    def setUp(self):
        user = User.objects.create_user('username', 'user@email.com', 'password')
        self.license = LicenseFactory(user=user, is_active=False)
        self.url = reverse('license:activate', args=[self.license.id])

    def test_get_logged_in(self):
        self.client.login(username='username', password='password')

        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('license:index'))

        license = License.objects.get(id=self.license.id)
        self.assertTrue(license.is_active)
