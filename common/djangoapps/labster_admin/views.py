import datetime

from weasyprint import HTML, CSS

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views import generic

from dateutil.relativedelta import relativedelta

from labster_admin.forms import TeacherToLicenseForm, DuplicateMultipleCourseForm

from labster_backoffice.models import Voucher, Payment, PaymentProduct, License
from labster_backoffice.forms import VoucherForm, StripePaymentForm, LicenseForm
from labster_backoffice.helpers import send_invoice_mail, send_confirmation_mail


def is_staff(user):
    return user.is_authenticated() and user.is_staff


class StaffMixin(object):

    @method_decorator(user_passes_test(is_staff))
    def dispatch(self, *args, **kwargs):
        return super(StaffMixin, self).dispatch(*args, **kwargs)


class Home(StaffMixin, generic.TemplateView):
    template_name = "labster_admin/home.html"


class AddTeacherToLicense(StaffMixin, generic.FormView):
    template_name = "labster_admin/add_teacher_to_license.html"
    form_class = TeacherToLicenseForm

    def get_success_url(self):
        return reverse('labster_add_teacher_to_license')

    def get_context_data(self, **kwargs):
        context = super(AddTeacherToLicense, self).get_context_data(**kwargs)
        context['is_add_teacher_to_license'] = True
        return context

    def form_valid(self, form):
        user, course_ids = form.save()
        for course_id in course_ids:
            messages.success(
                self.request,
                "<strong>{}</strong> is added to <strong>{}</strong>".format(user, course_id))
        return super(AddTeacherToLicense, self).form_valid(form)


class DuplicateMultipleCourse(StaffMixin, generic.FormView):
    template_name = "labster_admin/duplicate_multiple_courses.html"
    form_class = DuplicateMultipleCourseForm

    def get_success_url(self):
        return reverse('labster_duplicate_multiple_courses')

    def get_context_data(self, **kwargs):
        context = super(DuplicateMultipleCourse, self).get_context_data(**kwargs)
        context['is_duplicate_multiple_courses'] = True
        return context

    def form_valid(self, form):
        user = form.save(request=self.request)
        messages.success(
            self.request,
            "You have successfully duplicate course for <strong>{}</strong>".format(user))

        return super(DuplicateMultipleCourse, self).form_valid(form)


home = Home.as_view()
add_teacher_to_license = AddTeacherToLicense.as_view()
duplicate_multiple_courses = DuplicateMultipleCourse.as_view()


# Start from here is code for Labster BackOffice, views is in edX while urls, models, and templates are in another repo

def home(request):
    return HttpResponseRedirect(reverse('license:index'))


class IndexView(StaffMixin, generic.ListView):
    template_name = "vouchers/index.html"
    context_object_name = 'voucher_list'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['keyword'] = self.request.GET.get('keyword', '')
        return context

    def get_queryset(self):
        """ Return the list of voucher. """
        result = Voucher.objects.all().order_by('-id')

        keyword = self.request.GET.get('keyword')
        if keyword:
            result = result.filter(
                Q(id__icontains=keyword)
            )

        return result


class VoucherCreate(StaffMixin, generic.CreateView):
    form_class = VoucherForm
    template_name = "vouchers/create.html"

    def get_success_url(self):
        return reverse('voucher:index')


class VoucherUpdate(StaffMixin, generic.UpdateView):
    model = Voucher
    form_class = VoucherForm
    template_name = "vouchers/update.html"

    def get_success_url(self):
        return reverse('voucher:index')

    def get_context_data(self, **kwargs):

        context = super(VoucherUpdate, self).get_context_data(**kwargs)
        context['action'] = reverse('voucher:update', kwargs={'pk': self.get_object().id})

        return context


class VoucherDelete(StaffMixin, generic.DeleteView):
    model = Voucher
    template_name = "vouchers/delete.html"

    def get_success_url(self):
        return reverse('voucher:index')


class PaymentIndexView(StaffMixin, generic.ListView):
    template_name = "payment/index.html"
    context_object_name = 'payment_list'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(PaymentIndexView, self).get_context_data(**kwargs)
        context['keyword'] = self.request.GET.get('keyword', '')
        return context

    def get_queryset(self):
        """ Return the list of payment. """
        result =  PaymentProduct.objects.all().order_by('-id')

        keyword = self.request.GET.get('keyword')
        if keyword:
            result = result.filter(
                Q(payment__user__email__icontains=keyword) | Q(payment__user__username__icontains=keyword)
            )

        return result


# FIXME: deprecated
class PaymentCreate(StaffMixin, generic.CreateView):
    # form_class = PaymentForm
    from_class = forms.ModelForm
    model = Payment
    template_name = "payment/buy_lab.html"

    def get_success_url(self):
        return reverse('payment:index')

    def get_context_data(self, **kwargs):
        context = super(PaymentCreate, self).get_context_data(**kwargs)
        context['action'] = reverse('payment:buy_lab')

        return context

    def get_form_kwargs(self, **kwargs):
        form_kwargs = super(PaymentCreate, self).get_form_kwargs(**kwargs)
        # form_kwargs['account'] = self.request.user
        # form_kwargs['request'] = self.request
        return form_kwargs


class PaymentDetail(StaffMixin, generic.DetailView):
    model = Payment
    template_name = 'payment/detail.html'


@login_required
def activate_payment_view(request, payment_id):
    return HttpResponseRedirect(reverse('payment:index'))

    # FIXME: updating DB should use POST
    if payment_id:
        payment = get_object_or_404(Payment, id=payment_id)

        # Set the payment to paid state
        change_to_paid(payment)

        # Change the month subscription to date and add it to date_end_license
        date_end_license = payment.paid_at + relativedelta(months=+payment.month_subscription)

        # Add data to license
        valid_license = License(account=payment.account, lab=payment.labs, license_count=payment.license_count,
                                month_subscription=payment.month_subscription, date_bought=payment.paid_at,
                                date_end_license=date_end_license, is_active=True)
        valid_license.save()

        return HttpResponseRedirect(reverse('payment:index'))


@login_required
def charge(request, payment_id):
    return HttpResponse(200)

    if request.method == "POST":
        form = StripePaymentForm(request.POST, payment_id=payment_id)

        if form.is_valid():  # charges the card
            payment = Payment.objects.get(pk=payment_id)
            # Set the payment to paid
            change_to_paid(payment)
            send_confirmation_mail(payment)
            return render_to_response("payment/finish_payment.html",
                                      RequestContext(request, {'payment': payment}))
    else:
        form = StripePaymentForm(payment_id=payment_id)

    return render_to_response("payment/charge.html",
                              RequestContext(request, {'form': form}))


@login_required
def send_invoice_view(request, pk):
    return HttpResponse(200)

    # FIXME: should be POST
    """ Send invoice using email and send report using Json.  """
    response_data = {}
    response_data['success'] = True

    try:
        payment = Payment.objects.get(pk=pk)
        link_to_payment = reverse("payment:detail", args=[pk])
        link_to_payment = request.build_absolute_uri(link_to_payment)
        send_invoice_mail(link_to_payment, payment)
    except Payment.DoesNotExist:
        success = False

    return HttpResponse(response_data, content_type="application/json")


def change_to_paid(payment):
    payment.paid = True
    payment.paid_at = datetime.datetime.now()
    payment.save()


class PaymentDetailPDF(generic.View):

    def get(self, request, *args, **kwargs):
        return HttpResponse(200)

        context = {
        }
        rendered = render_to_string('payment/detail_pdf.html', context)

        if request.GET.get('d'):
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="test_pdf.pdf"'

            css = CSS(string='@page { size: A4; margin: 1cm }')
            html = HTML(string=rendered)
            html.write_pdf(response)
            return response

        else:
            return HttpResponse(rendered)


class LicenseIndexView(StaffMixin, generic.ListView):
    template_name = "license/index.html"
    context_object_name = 'license_list'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(LicenseIndexView, self).get_context_data(**kwargs)
        context['keyword'] = self.request.GET.get('keyword', '')
        return context

    def get_queryset(self):
        """ Return the list of license. """
        result = License.objects.all().order_by('-id')

        keyword = self.request.GET.get('keyword')
        if keyword:
            result = result.filter(
                Q(user__email__icontains=keyword) | Q(user__username__icontains=keyword)
            )

        return result


class LicenseCreate(StaffMixin, generic.CreateView):
    template_name = "license/form.html"
    model = License
    form_class = LicenseForm

    def get_success_url(self):
        return reverse('license:index')


class LicenseUpdate(StaffMixin, generic.UpdateView):
    template_name = "license/form.html"
    model = License
    form_class = LicenseForm

    def get_success_url(self):
        return reverse('license:index')


@login_required
def deactivate_license_view(request, license_id):
    # FIXME: updating DB should use POST
    if license_id:
        license_data = get_object_or_404(License, id=license_id)
        license_data.is_active = False
        license_data.save()

        return HttpResponseRedirect(reverse('license:index'))
    else:
        return HttpResponseRedirect(reverse('license:index'))


@login_required
def activate_license_view(request, license_id):
    # FIXME: updating DB should use POST
    if license_id:
        license_data = get_object_or_404(License, id=license_id)
        license_data.is_active = True
        license_data.save()

        return HttpResponseRedirect(reverse('license:index'))