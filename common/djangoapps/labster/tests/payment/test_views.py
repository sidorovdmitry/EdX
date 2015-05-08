import unittest

from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase

from labster.tests.factories import PaymentFactory
from labster.tests.views import ViewTestMixin


@unittest.skipUnless(settings.ROOT_URLCONF == 'cms.urls', 'Test only valid in cms')
class PaymentListTest(ViewTestMixin, TestCase):

    def setUp(self):
        self.url = reverse('labster-backoffice:payment:index')
        User.objects.create_user('username', 'user@email.com', 'password')


@unittest.skipUnless(settings.ROOT_URLCONF == 'cms.urls', 'Test only valid in cms')
class PaymentCreateTest(ViewTestMixin, TestCase):

    def setUp(self):
        User.objects.create_user('username', 'user@email.com', 'password')
        self.url = reverse('labster-backoffice:payment:buy_lab')


@unittest.skipUnless(settings.ROOT_URLCONF == 'cms.urls', 'Test only valid in cms')
class PaymentDetailTest(ViewTestMixin, TestCase):

    def setUp(self):
        User.objects.create_user('username', 'user@email.com', 'password')
        self.payment = PaymentFactory()
        self.url = reverse('labster-backoffice:payment:detail', args=[self.payment.id])


@unittest.skipUnless(settings.ROOT_URLCONF == 'cms.urls', 'Test only valid in cms')
class ActivatePaymentTest(ViewTestMixin, TestCase):

    def setUp(self):
        User.objects.create_user('username', 'user@email.com', 'password')
        self.payment = PaymentFactory()
        self.url = reverse('labster-backoffice:payment:activate', args=[self.payment.id])

    def test_get_logged_in(self):
        self.client.login(username='username', password='password')

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)


@unittest.skipUnless(settings.ROOT_URLCONF == 'cms.urls', 'Test only valid in cms')
class ChargePaymentTest(ViewTestMixin, TestCase):

    def setUp(self):
        User.objects.create_user('username', 'user@email.com', 'password')
        self.payment = PaymentFactory()
        self.url = reverse('labster-backoffice:payment:charge', args=[self.payment.id])


@unittest.skipUnless(settings.ROOT_URLCONF == 'cms.urls', 'Test only valid in cms')
class SendInvoiceTest(ViewTestMixin, TestCase):

    def setUp(self):
        User.objects.create_user('username', 'user@email.com', 'password')
        self.payment = PaymentFactory()
        self.url = reverse('labster-backoffice:payment:send_invoice', args=[self.payment.id])


@unittest.skipUnless(settings.ROOT_URLCONF == 'cms.urls', 'Test only valid in cms')
class PaymentDetailPDFTest(ViewTestMixin, TestCase):

    def setUp(self):
        User.objects.create_user('username', 'user@email.com', 'password')
        self.payment = PaymentFactory()
        self.url = reverse('labster-backoffice:payment:detail-pdf', args=[self.payment.id])

    def test_get_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
