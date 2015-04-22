from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views.generic import FormView

from labster_backoffice.csv_forms import UploadCsvProductForm, UploadCsvProductGroupForm, \
    UploadCsvVatForm

from labster_admin.views import StaffMixin


class UploadCsvProduct(StaffMixin, FormView):
    template_name = "product/upload_csv_product.html"
    form_class = UploadCsvProductForm

    def get_success_url(self):
        return reverse('labster-backoffice:product:upload-csv-product')

    def get_context_data(self, **kwargs):
        context = super(UploadCsvProduct, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        form.save()

        messages.success(self.request, "We have imported all of the products")

        return super(UploadCsvProduct, self).form_valid(form)


class UploadCsvProductGroup(StaffMixin, FormView):
    template_name = "product/upload_csv_product_group.html"
    form_class = UploadCsvProductGroupForm

    def get_success_url(self):
        return reverse('labster-backoffice:product:upload-csv-product-group')

    def get_context_data(self, **kwargs):
        context = super(UploadCsvProductGroup, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        form.save()

        messages.success(self.request, "We have imported all of the product groups")

        return super(UploadCsvProductGroup, self).form_valid(form)


class UploadCsvVat(StaffMixin, FormView):
    template_name = "vat/upload_vat.html"
    form_class = UploadCsvVatForm

    def get_success_url(self):
        return reverse('labster-backoffice:vat:upload-csv-vat')

    def get_context_data(self, **kwargs):
        context = super(UploadCsvVat, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        form.save()

        messages.success(self.request, "We have imported all of the vat")

        return super(UploadCsvVat, self).form_valid(form)
