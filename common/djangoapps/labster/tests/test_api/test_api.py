import json
from diplomat.models import ISOCountry
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone
from labster_backoffice.products.models import Product
from labster_backoffice.tests.factories import ProductFactory, UserFactory, ProductGroupFactory, \
    LicenseFactory, PaymentFactory, PaymentProductFactory
from rest_framework.authtoken.models import Token


def get_auth_header(user):
    token, _ = Token.objects.get_or_create(user=user)
    return {
        'HTTP_AUTHORIZATION': "Token {}".format(token.key),
    }


class NoGetMixin(object):

    def test_get_not_allowed(self):
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, 405)


class AuthGetOnlyMixin(object):

    def test_get_not_found(self):
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, 404)

    def test_get_not_authenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)


class AuthPostOnlyMixin(object):

    def test_post_not_authentication(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 401)


class CreateListProductsTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.product = ProductFactory()
        self.url = reverse('api:product')
        self.headers = get_auth_header(self.user)

    def test_get_found(self):
        ProductFactory()
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, 200)

    def test_post_new(self):
        post_data = {
            "name": "cytogenetics",
            "description": "cytogenetics description",
            "price": 19.99,
            "product_type": "univ",
            "month_subscription": 4,
            "image_url": "https://labsterim.s3.amazonaws.com/CACHE/images/media/uploads/ips/ips_title_image/0dea1fa00462af7336f7367ad3a62080.jpg",
            "is_active": True,
            "source_name": "labster",
            "external_id": 42,
        }

        response = self.client.post(self.url, post_data, **self.headers)
        self.assertEqual(response.status_code, 201)

        product = Product.objects.filter(external_id=self.product.external_id)
        self.assertEqual(product.count(), 2)


class CreateListProductGroupsTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.product = ProductFactory()
        self.product_group = ProductGroupFactory()
        self.url = reverse('api:product_group')
        self.headers = get_auth_header(self.user)

    def test_get_found(self):
        ProductGroupFactory()
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, 200)

    def test_post_new(self):
        ProductFactory()
        post_data = {
            "name": 'group',
            "price": 15,
            "products": [self.product]
        }

        response = self.client.post(self.url, post_data, **self.headers)
        self.assertEqual(response.status_code, 201)

        product = Product.objects.filter(id=self.product_group.id)
        self.assertEqual(product.count(), 1)


class ListLicenseTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.payment_product = PaymentProductFactory()
        self.url = reverse('api:list-license')
        self.headers = get_auth_header(self.user)

    def test_get_found(self):
        LicenseFactory(user=self.user, payment_product=self.payment_product)
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, 200)

    def test_post_new(self):
        UserFactory()
        PaymentProductFactory()
        post_data = {
            "user": [self.user],
            "price": 15,
            "payment_product": [self.payment_product],
            'date_bought': timezone.now(),
            'date_end_license': timezone.now(),
        }

        response = self.client.post(self.url, post_data, **self.headers)
        # Since this api only support get call it should return 405 Method Not Allowed
        self.assertEqual(response.status_code, 405)


class ListPaymentTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.payment = PaymentFactory()
        self.url = reverse('api:list-payment')
        self.headers = get_auth_header(self.user)

    def test_get_found(self):
        PaymentFactory()
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, 200)

    def test_detail_found(self):
        PaymentFactory()
        url = reverse('api:detail-payment', args=[self.payment.id])

        response = self.client.get(url, **self.headers)
        self.assertEqual(response.status_code, 200)


class CreatePaymentTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.payment = PaymentFactory()
        self.product = ProductFactory()
        self.url = reverse('api:create-payment')
        self.headers = get_auth_header(self.user)

    def test_post_new(self):
        UserFactory()
        ProductFactory()
        country = ISOCountry.objects.get(pk=1)
        list_product = [{'product': 1, 'item_count': 10, 'month_subscription': 5}]
        post_data = {
            "user": self.user.id,
            "payment_type": 'manual',
            "institution_type": 1,
            "institution_name": "",
            "country": country.id,
            "total_before_tax": 19.99,
            "vat_number": "",
            "list_product": list_product
        }

        response = self.client.post(self.url, json.dumps(post_data), content_type='application/json', **self.headers)
        self.assertEqual(response.status_code, 201)
