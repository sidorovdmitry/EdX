from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from labster_backoffice.models import License, deactivate_trial_licenses
from labster.tests.factories import (
    ProductFactory, ProductGroupFactory, PaymentProductFactory, LicenseFactory)


class LicenseModelTest(TestCase):

    def test_product_name_from_product(self):
        product = ProductFactory(name='Product')
        payment_product = PaymentProductFactory(product=product, product_group=None)
        LicenseFactory(payment_product=payment_product)
        license = License.objects.filter(payment_product=payment_product)[0]

        self.assertEqual(license.product_name, product.name)

    def test_product_name_from_product_group(self):
        product_group = ProductGroupFactory(name='Product Group')
        payment_product = PaymentProductFactory(product=None, product_group=product_group)
        LicenseFactory(payment_product=payment_product)
        license = License.objects.filter(payment_product=payment_product)[0]

        self.assertEqual(license.product_name, product_group.name)

    def test_trial_end_doesnt_exist(self):
        product = ProductFactory(name='Product')
        payment_product = PaymentProductFactory(product=product, product_group=None)
        LicenseFactory(payment_product=payment_product)
        license = License.objects.filter(payment_product=payment_product)[0]

        ten_days_ago = timezone.now() - timedelta(days=10)
        license.created_at = ten_days_ago
        license.is_active = True
        license.save()

        licenses = License.trial_end_objects.all()
        self.assertFalse(licenses.exists())

    def test_trial_end_exists(self):
        product = ProductFactory(name='Product')
        payment_product = PaymentProductFactory(product=product, product_group=None)
        LicenseFactory(payment_product=payment_product)
        license = License.objects.filter(payment_product=payment_product)[0]

        a_month_ago = timezone.now() - timedelta(days=14)
        license.date_bought = None
        license.created_at = a_month_ago
        license.is_active = True
        license.save()

        licenses = License.trial_end_objects.all()
        self.assertTrue(licenses.exists())

    def test_trial_end_exists_inactive(self):
        product = ProductFactory(name='Product')
        payment_product = PaymentProductFactory(product=product, product_group=None)
        LicenseFactory(payment_product=payment_product)
        license = License.objects.filter(payment_product=payment_product)[0]

        a_month_ago = timezone.now() - timedelta(days=30)
        license.created_at = a_month_ago
        license.is_active = False
        license.save()

        licenses = License.trial_end_objects.all()
        self.assertFalse(licenses.exists())

    def test_trial_end_exists_bought(self):
        product = ProductFactory(name='Product')
        payment_product = PaymentProductFactory(product=product, product_group=None)
        LicenseFactory(payment_product=payment_product)
        license = License.objects.filter(payment_product=payment_product)[0]

        a_month_ago = timezone.now() - timedelta(days=30)
        license.created_at = a_month_ago
        license.is_active = True
        license.date_bought = timezone.now()
        license.save()

        licenses = License.trial_end_objects.all()
        self.assertFalse(licenses.exists())

    def test_deactivate(self):
        product = ProductFactory(name='Product')
        payment_product = PaymentProductFactory(product=product, product_group=None)
        LicenseFactory(payment_product=payment_product)
        license = License.objects.filter(payment_product=payment_product)[0]

        a_month_ago = timezone.now() - timedelta(days=30)
        license.created_at = a_month_ago
        license.is_active = True
        license.save()

        deactivate_trial_licenses()
        licenses = License.trial_end_objects.all()
        self.assertFalse(licenses.exists())
