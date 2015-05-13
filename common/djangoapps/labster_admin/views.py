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
from django.views.generic import TemplateView, FormView, ListView, CreateView, \
    UpdateView, DeleteView, View, DetailView

from dateutil.relativedelta import relativedelta

from labster.users.forms import LabsterUserForm

from labster_admin.forms import TeacherToLicenseForm, DuplicateMultipleCourseForm

from labster_backoffice.models import Voucher, Payment, PaymentProduct, \
    License, CountryVat
from labster_backoffice.forms import VoucherForm, StripePaymentForm, \
    LicenseForm, ActivateDeactivateUserForm, UploadCsvVatForm
from labster_backoffice.helpers import send_invoice_mail, send_confirmation_mail

from labster.models import Lab


def is_staff(user):
    return user.is_authenticated() and user.is_staff


class StaffMixin(object):

    @method_decorator(user_passes_test(is_staff))
    def dispatch(self, *args, **kwargs):
        return super(StaffMixin, self).dispatch(*args, **kwargs)


class AddTeacherToLicense(StaffMixin, FormView):
    template_name = "labster_backoffice/add_teacher_to_license.html"
    form_class = TeacherToLicenseForm

    def get_success_url(self):
        return reverse('labster-backoffice:labster_add_teacher_to_license')

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


class DuplicateMultipleCourse(StaffMixin, FormView):
    template_name = "labster_backoffice/duplicate_multiple_courses.html"
    form_class = DuplicateMultipleCourseForm

    def get_success_url(self):
        return reverse('labster-backoffice:labster_duplicate_multiple_courses')

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


class ActivateDeactivateUser(StaffMixin, FormView):
    template_name = "user/activate_deactivate_user.html"
    form_class = ActivateDeactivateUserForm

    def get_success_url(self):
        return reverse('labster-backoffice:labster-activate-deactivate-user')

    def get_context_data(self, **kwargs):
        context = super(ActivateDeactivateUser, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        activate_user = form.save()

        if activate_user:
            messages.success(self.request, "The users have been activated")
        else:
            messages.success(self.request, "The users have been deactivated")

        return super(ActivateDeactivateUser, self).form_valid(form)


class VatIndexView(StaffMixin, ListView):
    template_name = "vat/index.html"
    context_object_name = 'country_vat_list'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(VatIndexView, self).get_context_data(**kwargs)
        context['keyword'] = self.request.GET.get('keyword', '')
        return context

    def get_queryset(self):
        """ Return the list of voucher. """
        result = CountryVat.objects.all().order_by('-id')

        keyword = self.request.GET.get('keyword')
        if keyword:
            result = result.filter(
                Q(country_code__icontains=keyword) | Q(country_name__icontains=keyword)
            )

        return result


class UploadCsvVat(StaffMixin, FormView):
    template_name = "vat/upload_vat.html"
    form_class = UploadCsvVatForm

    def get_success_url(self):
        return reverse('labster-backoffice:vat:upload-vat')

    def get_context_data(self, **kwargs):
        context = super(UploadCsvVat, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        form.save()

        messages.success(self.request, "We have import all of the countries vat")

        return super(UploadCsvVat, self).form_valid(form)


class CreateLabsterUser(StaffMixin, FormView):
    template_name = "user/create_user.html"
    form_class = LabsterUserForm

    def get_success_url(self):
        return reverse('labster-backoffice:labster-create-user')

    def get_context_data(self, **kwargs):
        context = super(CreateLabsterUser, self).get_context_data(**kwargs)
        return context

    def form_valid(self,form):
        labster_user = form.save()

        messages.success(
            self.request,
            "You have successfully created user for <strong>{}</strong>".format(labster_user.user))


def home(request):
    return HttpResponseRedirect(reverse('labster-backoffice:license:index'))


class IndexView(StaffMixin, ListView):
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


class VoucherCreate(StaffMixin, CreateView):
    form_class = VoucherForm
    template_name = "vouchers/create.html"

    def get_success_url(self):
        return reverse('labster-backoffice:voucher:index')


class VoucherUpdate(StaffMixin, UpdateView):
    model = Voucher
    form_class = VoucherForm
    template_name = "vouchers/update.html"

    def get_success_url(self):
        return reverse('labster-backoffice:voucher:index')

    def get_context_data(self, **kwargs):

        context = super(VoucherUpdate, self).get_context_data(**kwargs)
        context['action'] = reverse('labster-backoffice:voucher:update', kwargs={'pk': self.get_object().id})

        return context


class VoucherDelete(StaffMixin, DeleteView):
    model = Voucher
    template_name = "vouchers/delete.html"

    def get_success_url(self):
        return reverse('labster-backoffice:voucher:index')


class PaymentIndexView(StaffMixin, ListView):
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
class PaymentCreate(StaffMixin, CreateView):
    # form_class = PaymentForm
    from_class = forms.ModelForm
    model = Payment
    template_name = "payment/buy_lab.html"

    def get_success_url(self):
        return reverse('labster-backoffice:payment:index')

    def get_context_data(self, **kwargs):
        context = super(PaymentCreate, self).get_context_data(**kwargs)
        context['action'] = reverse('labster-backoffice:payment:buy_lab')

        return context

    def get_form_kwargs(self, **kwargs):
        form_kwargs = super(PaymentCreate, self).get_form_kwargs(**kwargs)
        # form_kwargs['account'] = self.request.user
        # form_kwargs['request'] = self.request
        return form_kwargs


class PaymentDetail(StaffMixin, DetailView):
    model = Payment
    template_name = 'payment/detail.html'


@login_required
def activate_payment_view(request, payment_id):
    return HttpResponseRedirect(reverse('labster-backoffice:payment:index'))

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

        return HttpResponseRedirect(reverse('labster-backoffice:payment:index'))


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
        link_to_payment = reverse("labster-backoffice:payment:detail", args=[pk])
        link_to_payment = request.build_absolute_uri(link_to_payment)
        send_invoice_mail(link_to_payment, payment)
    except Payment.DoesNotExist:
        success = False

    return HttpResponse(response_data, content_type="application/json")


def change_to_paid(payment):
    payment.paid = True
    payment.paid_at = datetime.datetime.now()
    payment.save()


class PaymentDetailPDF(View):

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


class LicenseIndexView(StaffMixin, ListView):
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


class LicenseCreate(StaffMixin, CreateView):
    template_name = "license/form.html"
    model = License
    form_class = LicenseForm

    def get_success_url(self):
        return reverse('labster-backoffice:license:index')


class LicenseUpdate(StaffMixin, UpdateView):
    template_name = "license/form.html"
    model = License
    form_class = LicenseForm

    def get_success_url(self):
        return reverse('labster-backoffice:license:index')


@login_required
def deactivate_license_view(request, license_id):
    # FIXME: updating DB should use POST
    if license_id:
        license_data = get_object_or_404(License, id=license_id)
        license_data.is_active = False
        license_data.save()

        return HttpResponseRedirect(reverse('labster-backoffice:license:index'))
    else:
        return HttpResponseRedirect(reverse('labster-backoffice:license:index'))


@login_required
def activate_license_view(request, license_id):
    # FIXME: updating DB should use POST
    if license_id:
        license_data = get_object_or_404(License, id=license_id)
        license_data.is_active = True
        license_data.save()

        return HttpResponseRedirect(reverse('labster-backoffice:license:index'))


class LabsPlayData(StaffMixin, TemplateView):
    template_name = "labster_admin/lab_plays_data.html"

    def get_context_data(self, **kwargs):
        context = super(LabsPlayData, self).get_context_data(**kwargs)
        context['labs'] = Lab.objects.order_by('name')
        return context


add_teacher_to_license = AddTeacherToLicense.as_view()
duplicate_multiple_courses = DuplicateMultipleCourse.as_view()
activate_deactivate_user = ActivateDeactivateUser.as_view()
upload_vat = UploadCsvVat.as_view()
index_vat = VatIndexView.as_view()
create_labster_user = CreateLabsterUser.as_view()
labs_play_data = LabsPlayData.as_view()
