from django.test import TestCase
from django.utils import timezone

from labster.tests.factories import LicenseFactory, UserFactory, PaymentProductFactory
from labster_backoffice.forms import LicenseForm
from labster_backoffice.models import License


class LicenseFormTest(TestCase):

    def test_valid(self):
        date_end = timezone.now()
        user = UserFactory()
        payment_product = PaymentProductFactory()
        data = {
            'user': user.id,
            'item_count': 3,
            'date_bought': date_end,
            'date_end_license': date_end,
            'is_active': 1,
            'voucher_code': "",
            'payment_product': payment_product.id
        }

        form = LicenseForm(data)
        self.assertTrue(form.is_valid())

    def test_save(self):
        date_end = timezone.now()
        user = UserFactory()
        payment_product = PaymentProductFactory()
        data = {
            'user': user.id,
            'item_count': 3,
            'date_bought': date_end,
            'date_end_license': date_end,
            'is_active': 1,
            'voucher_code': "",
            'payment_product': payment_product.id
        }

        form = LicenseForm(data)
        self.assertTrue(form.is_valid())

        license = form.save()
        license = License.objects.get(id=license.id)        

        self.assertEqual(license.item_count, data['item_count'])
        self.assertEqual(license.is_active, data['is_active'])
