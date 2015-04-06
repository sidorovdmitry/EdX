from django.contrib.auth.models import User
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase

from labster_backoffice.tests.factories import PaymentFactory
from labster_backoffice.tests.views import ViewTestMixin


class PaymentListTest(ViewTestMixin, TestCase):

    def setUp(self):
        self.url = reverse('payment:index')
        User.objects.create_user('username', 'user@email.com', 'password')


class PaymentCreateTest(ViewTestMixin, TestCase):

    def setUp(self):
        User.objects.create_user('username', 'user@email.com', 'password')
        self.url = reverse('payment:buy_lab')


class PaymentDetailTest(ViewTestMixin, TestCase):

    def setUp(self):
        User.objects.create_user('username', 'user@email.com', 'password')
        self.payment = PaymentFactory()
        self.url = reverse('payment:detail', args=[self.payment.id])


class ActivatePaymentTest(ViewTestMixin, TestCase):

    def setUp(self):
        User.objects.create_user('username', 'user@email.com', 'password')
        self.payment = PaymentFactory()
        self.url = reverse('payment:activate', args=[self.payment.id])

    def test_get_logged_in(self):
        self.client.login(username='username', password='password')

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)


class ChargePaymentTest(ViewTestMixin, TestCase):

    def setUp(self):
        User.objects.create_user('username', 'user@email.com', 'password')
        self.payment = PaymentFactory()
        self.url = reverse('payment:charge', args=[self.payment.id])


class SendInvoiceTest(ViewTestMixin, TestCase):

    def setUp(self):
        User.objects.create_user('username', 'user@email.com', 'password')
        self.payment = PaymentFactory()
        self.url = reverse('payment:send_invoice', args=[self.payment.id])


class PaymentDetailPDFTest(ViewTestMixin, TestCase):

    def setUp(self):
        User.objects.create_user('username', 'user@email.com', 'password')
        self.payment = PaymentFactory()
        self.url = reverse('payment:detail-pdf', args=[self.payment.id])

    def test_get_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
