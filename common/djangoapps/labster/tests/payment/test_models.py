from django.test import TestCase
from django.utils import timezone

from datetime import timedelta

from labster_backoffice.tests.factories import (
    ProductFactory, ProductGroupFactory, PaymentProductFactory, PaymentFactory)
from labster_backoffice.payments.models import send_reminder_emails, Payment


class PaymentProductModelTest(TestCase):

    def test_product_name_from_product(self):
        product = ProductFactory(name='Product')
        payment_product = PaymentProductFactory(product=product, product_group=None)

        self.assertEqual(payment_product.product_name, product.name)

    def test_product_name_from_product_group(self):
        product_group = ProductGroupFactory(name='Product Group')
        payment_product = PaymentProductFactory(product=None, product_group=product_group)

        self.assertEqual(payment_product.product_name, product_group.name)


class PaymentModelTest(TestCase):

    def test_send_reminder_emails(self):
        eight_days_ago = timezone.now() - timedelta(days=8)
        payment = PaymentFactory()
        payment.created_at = eight_days_ago
        payment.last_reminder_at = timezone.now() - timedelta(days=7)
        payment.save()
        send_reminder_emails()

        edited_payment = Payment.objects.get(id=payment.id)
        self.assertEqual(edited_payment.last_reminder_at.date(), timezone.now().date())

    def test_send_reminder_email_active(self):
        # if payment is still active then keep sending email reminder
        payment = PaymentFactory()

        response = payment.send_reminder_email()
        self.assertEqual(response, True)

    def test_send_reminder_email_inactive(self):
        payment = PaymentFactory()
        # cancelinng payment, set to inactive
        payment.is_active = False

        response = payment.send_reminder_email()
        # if payment has been cancelled, don't send email anymore
        self.assertEqual(response, False)

    def test_send_reminder_email_paid(self):
        payment = PaymentFactory()
        # cancelinng payment, set to inactive
        payment.paid = True
        payment.paid_at = timezone.now().date()

        response = payment.send_reminder_email()
        # if payment has been cancelled, don't send email anymore
        self.assertEqual(response, False)
