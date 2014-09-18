from django import forms
from django.core.urlresolvers import reverse


class PaymentForm(forms.Form):
    subscription_choices = (
        ('6', '1 semester'),
        ('12', '1 year'),
    )

    LAB_TYPE_CHOICES = (
        ('all_lab', 'All lab'),
        ('some_lab', 'Some lab'),
    )

    PAYMENT_TYPE_CHOICES = (
        ('manual', 'Manual'),
        ('stripe', 'Stripe'),
    )
    # payment_type = forms.CharField(max_length=6, choices=PAYMENT_TYPE_CHOICES, default='manual')
    # lab_buy_type = forms.ChoiceField(required=False, choices=LAB_TYPE_CHOICES)
    # labs = forms.MultipleChoiceField(required=False, choices=(), widget=forms.CheckboxSelectMultiple)
    month_subscription = forms.ChoiceField(required=False, choices=subscription_choices)
    total = forms.DecimalField(decimal_places=2, max_digits=10)

    def save(self, *args, **kwargs):
        data = self.cleaned_data
        kwargs['commit'] = False
        instance = super(PaymentForm, self).save(*args, **kwargs)
        # instance.account = self.account

        # calculate the total invoice
        # lab_buy_type = data.get('lab_buy_type')
        # license_count = int(data.get('license_count'))
        # we need to divide the month subscription by one semester
        month_subscription = int(data.get('month_subscription')) / 6

        # if lab_buy_type == 'all_lab':
        #     labs = Lab.objects.all()
        #     # $50/all labs/user/semester
        #     total = license_count * month_subscription * 50
        # else:
        #     # Count how many labs in the form
        #     labs = Lab.objects.filter(pk__in=data.get('labs'))
        #     lab_count = labs.count()
        #     # $20/labs/user/semester
        #     total = license_count * month_subscription * lab_count * 20
        # if total >= 500:
        #     # Set the payment type to manual if the invoice is more than $500
        #     instance.payment_type = 'Manual'
        # instance.total = total
        # instance.save()
        #
        # for lab in labs:
        #     instance.labs.add(lab)
        #
        # # send email after payment
        # link_to_payment = reverse("payment:detail", args=[instance.id])
        # link_to_payment = self.request.build_absolute_uri(link_to_payment)
        # send_invoice_mail(link_to_payment, instance)