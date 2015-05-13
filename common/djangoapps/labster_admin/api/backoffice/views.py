import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from rest_framework import status
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView, ListAPIView, ListCreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from diplomat.models import ISOCountry

from labster_backoffice.api.serializers import PaymentSerializer, PaymentStripeSerializer, \
    ProductSerializer, PaymentListSerializer, LicenseListSerializer, \
    ProductGroupSerializer, CountrySerializer, PaymentProductMinSerializer, UserLicenseSerializer, VoucherSerializer, \
    PaymentModelSerializer, CountryVatSerializer

from labster_backoffice.models import Payment, PaymentProduct, PaymentStripe, License, Product, ProductGroup, Voucher, \
    CountryVat
from labster_backoffice.models import create_license


class AuthMixin:
    def __init__(self):
        pass

    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticatedOrReadOnly,)


class UserToken(APIView):

    def get(self, request, *args, **kwargs):
        response_data = {}

        try:
            existing_user = User.objects.get(id=self.kwargs['user_id'])
            http_status = status.HTTP_200_OK
            token, _ = Token.objects.get_or_create(user=existing_user)
            response_data.update({
                'id': existing_user.id,
                'token': token.key
            })
        except User.DoesNotExist:
            http_status = status.HTTP_204_NO_CONTENT
            response_data.update({
                'token': token.key
            })

        return Response(response_data)


class GetRenewLicenseBill(AuthMixin, APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        response_data = {}

        licenses_id = self.request.QUERY_PARAMS.get('licenses_id')
        user_id = self.request.QUERY_PARAMS.get('user_id')
        licenses_id = licenses_id.split('+')
        licenses_id = filter(None, licenses_id)
        last_payment = Payment.objects.filter(user=user_id).latest('id')
        country = CountrySerializer(last_payment.country)
        institution_type = last_payment.institution_type
        institution_name = last_payment.institution_name
        vat_number = last_payment.vat_number
        total_before_tax = 0

        products = []
        for license_id in licenses_id:
            license = License.objects.get(id=license_id)

            payment_product = license.payment_product
            product = PaymentProductMinSerializer(payment_product)
            products.append(product.data)
            price = payment_product.product_price
            subtotal = payment_product.item_count * price
            total_before_tax += subtotal

        response_data.update({
            'country': country.data,
            'products': products,
            'institution_type': institution_type,
            'institution_name': institution_name,
            'vat_number': vat_number,
            'total_before_tax': total_before_tax
        })

        return Response(response_data)


class CancelOrder(AuthMixin, APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        payment_id = self.kwargs['pk']
        user = self.request.user
        payments = Payment.objects.filter(user=user)
        payment_serializer = PaymentListSerializer(payments, many=True)

        response_data = {}
        response_data.update({
            'payments': payment_serializer.data,
            'payment_id': payment_id
        })

        return Response(response_data)

    def post(self, request, *args, **kwargs):
        payment_id = self.kwargs['pk']
        user = self.request.user

        payment = get_object_or_404(Payment, pk=payment_id)
        payment.is_active = False
        payment.save()

        payment_products = PaymentProduct.objects.filter(payment=payment)

        licenses = License.objects.filter(payment_product__in=payment_products)
        for license in licenses:
            license.is_active = False
            license.save()

        http_status = status.HTTP_200_OK

        return Response(http_status)


class CreatePayment(AuthMixin, CreateAPIView):
    model = Payment
    serializer_class = PaymentSerializer
    permission_classes = (IsAuthenticated,)

    def pre_save(self, obj):
        # Set total to 0 first because we haven't set the payment product of this payment
        obj.total = 0
        obj.total_before_tax = 0

    def post_save(self, obj, created=False):
        payment = get_object_or_404(Payment, pk=obj.id)
        is_renew = self.request.DATA.get('is_renew')
        is_teacher = self.request.DATA.get('is_teacher')
        license_id = self.request.DATA.get('license_id')
        list_product = self.request.DATA.get('list_product', [])
        for item in list_product:
            product = None
            product_group = None
            price = None
            try:
                product = get_object_or_404(Product, pk=item["product"])
                price = product.price
            except KeyError:
                pass
            try:
                product_group = get_object_or_404(ProductGroup, pk=item["product_group"])
                price = product_group.price
            except KeyError:
                pass

            payment_product = PaymentProduct(product=product, product_group=product_group, payment=payment,
                                             price=price, item_count=item["item_count"],
                                             month_subscription=item["month_subscription"])
            payment_product.save()


            if is_renew is None and is_teacher:
                # create trial license, only create trial license for teacher
                create_license(payment_product)
            elif license_id:
                # assign existing license to this payment_product
                existing_license = License.objects.get(pk=license_id)
                existing_license.payments.add(payment)
                existing_license.payment_product = payment_product
                existing_license.save()

        # We have the list of payment group of this payment. Time to count total payment
        payment.vat = payment.get_vat_percent()
        payment.total_before_tax = payment.get_total()
        payment.total = payment.get_total_after_tax()
        payment.save()

        if payment.is_manual:
            payment.send_invoice_email()


class CreatePaymentVoucherCode(AuthMixin, CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response_data = {}
        data = request.DATA
        voucher = get_object_or_404(Voucher, id=data['voucher_code'])
        try:
            # if the student has used the voucher code before just return the object
            existing_payment = Payment.objects.get(user_id=data['user'], voucher_code=data['voucher_code'])
            http_status = status.HTTP_200_OK
            payment_serializer = PaymentModelSerializer(existing_payment)
            voucher_serializer = VoucherSerializer(voucher)
            response_license_id = 0
        except Payment.DoesNotExist:
            # if the limit has been reached
            if voucher.limit <= voucher.used_count:
                http_status = status.HTTP_204_NO_CONTENT
                response_data.update({
                    'limit_reached': True,
                })
                return Response(response_data, http_status)
            else:
                # update the count
                voucher.used_count += 1
                voucher.save()

            try:
                country = ISOCountry.objects.get(alpha2=data['country'])
            except ISOCountry.DoesNotExist:
                country = None

            # create payment
            payment = Payment(
                user_id=data['user'], payment_type="stripe", institution_type=1,
                total=0, total_before_tax=0, country=country, voucher_code=voucher.id)
            payment.save()

            # Create payment_product
            for item in voucher.products.all():
                product = get_object_or_404(Product, pk=item.id)
                price = product.price

                payment_product = PaymentProduct(product=product, payment=payment,
                                                 price=price, item_count=1,
                                                 month_subscription=product.month_subscription)
                payment_product.save()

                # If voucher price is 0, set the payment to paid already
                parent_license = None
                if voucher.price == 0:
                    # Search parent license to be linked
                    try:
                        parent_license = License.objects.get(voucher_code=voucher.id)
                    except License.DoesNotExist:
                        pass

                    license_product = License(user=request.user, payment_product=payment_product, is_active=True, \
                        item_count=payment_product.item_count, item_used=1, date_bought=timezone.now(), \
                        created_at=timezone.now(), parent_license=parent_license)
                    license_product.date_end_license = timezone.now() + relativedelta(weeks=+voucher.week_subscription)
                    license_product.save()

            # We have the list of payment group of this payment. Time to count total payment
            payment.vat = payment.get_vat_percent()
            payment.total_before_tax = voucher.price
            payment.total = payment.get_total_after_tax()

            if voucher.price == 0:
                payment.paid = True
                payment.paid_at = timezone.now()
                payment.payment_type = "manual"
                # payment.send_payment_finished_email()

            payment.save()

            payment_serializer = PaymentModelSerializer(payment)
            voucher_serializer = VoucherSerializer(voucher)

            if parent_license:
                response_license_id = parent_license.id
            else:
                response_license_id = 0

            http_status = status.HTTP_201_CREATED

        response_data.update({
            'payment': payment_serializer.data,
            'voucher': voucher_serializer.data,
            'response_license_id': response_license_id,
            'limit_reached': False,
        })
        return Response(response_data, http_status)


class VoucherDetail(AuthMixin, RetrieveAPIView):
    serializer_class = VoucherSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        voucher_id = self.kwargs['pk']
        voucher = get_object_or_404(Voucher, pk=voucher_id)
        return voucher


class PaymentList(AuthMixin, ListAPIView):
    serializer_class = PaymentListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        paid_status = self.request.GET.get('status')
        if paid_status:
            return Payment.objects.filter(user=user, paid=paid_status, is_active=True)
        else:
            return Payment.objects.filter(user=user, is_active=True)


class PaymentDetail(AuthMixin, RetrieveAPIView):
    serializer_class = PaymentListSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        payment_id = self.kwargs['pk']
        payment = get_object_or_404(Payment, pk=payment_id)
        return payment


class GetInvoiceEmail(AuthMixin, APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        payment_id = self.kwargs['pk']
        payment = get_object_or_404(Payment, pk=payment_id)
        payment.send_invoice_email()

        http_status = status.HTTP_200_OK

        return Response(http_status)


class CreatePaymentStripe(AuthMixin, CreateAPIView):
    serializer_class = PaymentStripeSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        token = request.DATA.get('stripe_token')
        voucher_code = request.DATA.get('voucher_code')
        # licenses_id = request.DATA.get('licenses_id')
        payment_id = self.kwargs.get('pk')
        response_data = {}

        payment = get_object_or_404(Payment, pk=payment_id)
        payment_stripe = PaymentStripe(payment=payment)
        description = "Invoice paid by: {0}. Invoice number: {1}".format(payment.user.email, payment.invoice_number)

        # Charge in stripe
        success, payment_stripe_response = payment_stripe.charge(
            payment.total_in_cents, token, description, payment.user.email)

        if not success:
            response_data['status'] = False
            http_status = status.HTTP_400_BAD_REQUEST
        else:
            # Save the payment stripe object
            payment_stripe.save()

            # Update the payment
            payment.paid = True
            payment.paid_at = timezone.now()
            payment.payment_type = "stripe"
            payment.save()

            # Add data to license model
            payment_products = PaymentProduct.objects.filter(payment=payment)
            for payment_product in payment_products:

                try:
                    license_product = License.objects.get(user=user, payment_product=payment_product)
                    if payment.voucher_code:
                        # if using voucher, use the subscription from it instead
                        voucher = get_object_or_404(Voucher, pk=payment.voucher_code)
                        date_end_license = payment.paid_at + relativedelta(weeks=+voucher.week_subscription)
                    else:
                        if license_product.date_end_license < timezone.now() or license_product.date_bought is None:
                            # if the previous license has expired, we count date_end_license from datetime.now
                            # or if this is a new payment
                            date_end_license = payment.paid_at + relativedelta(months=+payment_product.month_subscription)
                        else:
                            # if the license still active, extend the date_end_license
                            date_end_license = license_product.date_end_license + relativedelta(
                                months=+license_product.month_subscription)
                except License.DoesNotExist:
                    license_product = License(user=user, payment_product=payment_product)
                    license_product.item_count = payment_product.item_count
                    if payment.voucher_code:
                        # if using voucher, use the subscription from it instead
                        voucher = get_object_or_404(Voucher, pk=payment.voucher_code)
                        date_end_license = payment.paid_at + relativedelta(weeks=+voucher.week_subscription)
                    else:
                        date_end_license = payment.paid_at + relativedelta(months=+payment_product.month_subscription)

                license_product.date_bought = payment.paid_at
                license_product.date_end_license = date_end_license
                license_product.is_active = True

                # user uses voucher
                # need to get parent license to be linked to here
                parent_license = None
                if voucher_code:
                    try:
                        parent_license = License.objects.get(voucher_code=voucher_code)
                    except License.DoesNotExist:
                        # this shouldn't even happened
                        pass

                license_product.parent_license = parent_license
                license_product.save()
                license_product.payments.add(payment)

            if parent_license:
                response_license_id = parent_license.id
            else:
                response_license_id = license_product.id

            payment.send_invoice_email()
            http_status = status.HTTP_201_CREATED
            response_data.update({
                'status': True,
                'license_id': response_license_id,
            })
        return Response(response_data, http_status)


class CreateListProducts(AuthMixin, ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        product_type = self.request.GET.get('product_type')
        if product_type:
            return Product.objects.filter(product_type=product_type)
        else:
            return Product.objects.all()


class UpdateProduct(AuthMixin, UpdateAPIView):
    model = Product
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated,)


class GetProductByExternalId(AuthMixin, RetrieveAPIView):
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        external_id = self.kwargs['external_id']
        product_type = self.request.QUERY_PARAMS.get('product_type')
        product = get_object_or_404(Product, external_id=external_id, product_type=product_type)
        return product


class CreateListProductGroup(AuthMixin, ListCreateAPIView):
    serializer_class = ProductGroupSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        group_type = self.request.GET.get('group_type')
        if group_type:
            return ProductGroup.objects.filter(group_type=group_type)
        else:
            return ProductGroup.objects.all()


class LicenseList(AuthMixin, ListAPIView):
    serializer_class = LicenseListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return License.objects.filter(user=user, date_bought__isnull=False)


class CountryList(ListAPIView):
    # permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        countries = ISOCountry.objects.all()
        countries_serializer = CountrySerializer(countries, many=True)

        countries_vat = CountryVat.objects.all()
        countries_vat_serializer = CountryVatSerializer(countries_vat, many=True)

        response_data = {}
        response_data.update({
            'countries': countries_serializer.data,
            'countries_vat': countries_vat_serializer.data
        })

        return Response(response_data)



class CreateUserLicense(AuthMixin, CreateAPIView):
    serializer_class = UserLicenseSerializer
    permission_classes = (IsAuthenticated,)
