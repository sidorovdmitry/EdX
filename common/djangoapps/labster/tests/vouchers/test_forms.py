from django.test import TestCase

from labster.tests.factories import ProductFactory
from labster_backoffice.forms import VoucherForm
from labster_backoffice.models import Voucher, VoucherProduct


class VoucherFormTest(TestCase):

    def test_valid(self):
        products = [ProductFactory() for i in range(3)]
        product_ids = [p.id for p in products]
        data = {
            'id': "1234567890",
            'price': 10,
            'limit': 100,
            'week_subscription': 10,
            'products': product_ids,
            'all_labs': "Not All Labs",
        }

        form = VoucherForm(data)
        self.assertTrue(form.is_valid())

    def test_save(self):
        products = [ProductFactory() for i in range(3)]
        product_ids = [p.id for p in products]
        data = {
            'id': "1234567890",
            'price': 10,
            'limit': 100,
            'week_subscription': 10,
            'products': product_ids,
            'all_labs': "Not All Labs",
        }

        form = VoucherForm(data)
        form.is_valid()

        voucher = form.save()
        voucher = Voucher.objects.get(id=voucher.id)
        voucher_product = VoucherProduct.objects.get(voucher_code=voucher.id)
        products = voucher_product.products.all()

        self.assertItemsEqual(product_ids, [p.id for p in products])
