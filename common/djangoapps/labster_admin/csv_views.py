from django.views import generic
from django.contrib import messages

from labster_backoffice.csv_forms import UploadCsvProductForm
from labster_admin.views import StaffMixin


class UploadCsvProduct(StaffMixin, generic.FormView):
    template_name = "product/upload_csv.html"
    form_class = UploadCsvProductForm

    def get_success_url(self):
        return reverse('labster-backoffice:product:upload_csv')

    def get_context_data(self, **kwargs):
        context = super(UploadCsvProduct, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        form.save()

        messages.success(self.request, "We have imported all of the products")

        return super(UploadCsvVat, self).form_valid(form)
