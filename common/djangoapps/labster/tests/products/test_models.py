from django.test import TestCase

from labster_backoffice.products.models import Product
from labster_backoffice.payments.models import PaymentProduct
from labster_backoffice.tests.factories import (
    ProductFactory, PaymentFactory, ProductGroupFactory)


class ProductModelTest(TestCase):

    def setUp(self):
        self.inactive = ProductFactory(is_active=False)
        self.active = ProductFactory(is_active=True)

    def test_all(self):
        products = Product.objects.all()
        self.assertIn(self.active, products)
        self.assertIn(self.inactive, products)

    def test_active(self):
        products = Product.objects.active()
        self.assertIn(self.active, products)
        self.assertNotIn(self.inactive, products)


class PaymentProductModelTest(TestCase):

    def setUp(self):
        self.payment = PaymentFactory()
        self.product = ProductFactory()
        self.product_group = ProductGroupFactory()

    def test_save_no_product_at_all(self):
        obj = PaymentProduct(payment=self.payment, price=200)
        with self.assertRaises(AssertionError):
            obj.save()

    def test_with_product(self):
        obj = PaymentProduct(payment=self.payment, product=self.product, price=200)
        obj.save()

    def test_with_product_group(self):
        obj = PaymentProduct(payment=self.payment,
                             product_group=self.product_group,
                             price=200)
        obj.save()

    def test_with_both(self):
        """ this shouldn't even happened, but we don't have the solution yet """
        obj = PaymentProduct(payment=self.payment,
                             product=self.product,
                             product_group=self.product_group,
                             price=200)
        obj.save()
