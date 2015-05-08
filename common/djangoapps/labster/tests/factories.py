from django.utils import timezone
from django.contrib.auth.models import User

import factory
from factory.django import DjangoModelFactory

from labster_backoffice.models import Payment, PaymentProduct, License, \
    Product, ProductGroup, Voucher


class UserFactory(DjangoModelFactory):
    FACTORY_FOR = User
    # class Meta:
    #     model = User
    #     django_get_or_create = ('email', 'first_name', 'username')

    username = "batman"
    first_name = "bruce"
    email = "batman@labster.com"


class ProductFactory(DjangoModelFactory):
    FACTORY_FOR = Product
    # class Meta:
    #     model = Product
    #     django_get_or_create = ('name', 'price', 'description', 'is_active', 'source_name', 'image_url', 'external_id')

    name = factory.Sequence(lambda n: '{0} cytogenetics'.format(n))
    price = 15
    description = "cytogenetics description"
    is_active = True
    source_name = "labster"
    image_url = "https://labsterim.s3.amazonaws.com/CACHE/images/media/uploads/ips/ips_title_image/0dea1fa00462af7336f7367ad3a62080.jpg",
    external_id = "42"


class ProductGroupFactory(DjangoModelFactory):
    FACTORY_FOR = ProductGroup
    # class Meta:
    #     model = ProductGroup

    name = factory.Sequence(lambda n: '{0} group'.format(n))
    price = 15


class PaymentFactory(DjangoModelFactory):
    FACTORY_FOR = Payment
    # class Meta:
    #     model = Payment

    payment_type = 'stripe'
    total = 110
    vat = 10.0
    total_before_tax = 100
    user = factory.SubFactory(UserFactory)
    invoice_pdf = factory.django.FileField(filename="invoice.pdf")
    is_active = True


class PaymentProductFactory(DjangoModelFactory):
    FACTORY_FOR = PaymentProduct
    # class Meta:
    #     model = PaymentProduct

    price = 10
    month_subscription = 12
    item_count = 10
    product = factory.SubFactory(ProductFactory)
    product_group = factory.SubFactory(ProductGroupFactory)
    payment = factory.SubFactory(PaymentFactory)


class LicenseFactory(DjangoModelFactory):
    FACTORY_FOR = License
    # class Meta:
    #     model = License

    user = factory.SubFactory(UserFactory)
    payment_product = factory.SubFactory(PaymentProductFactory)
    date_bought = timezone.now()
    date_end_license = timezone.now()


class VoucherFactory(DjangoModelFactory):
    FACTORY_FOR = Voucher
    # class Meta:
    #     model = Voucher

    id = factory.Sequence(lambda n: "abc{0}defghi".format(n))
    price = 100
