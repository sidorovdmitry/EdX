from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, FormView

from labster_admin.forms import TeacherToLicenseForm


def is_staff(user):
    return user.is_authenticated() and user.is_staff


class StaffMixin(object):

    @method_decorator(user_passes_test(is_staff))
    def dispatch(self, *args, **kwargs):
        return super(StaffMixin, self).dispatch(*args, **kwargs)


class Home(StaffMixin, TemplateView):
    template_name = "labster_admin/home.html"


class AddTeacherToLicense(StaffMixin, FormView):
    template_name = "labster_admin/add_teacher_to_license.html"
    form_class = TeacherToLicenseForm

    def get_context_data(self, **kwargs):
        context = super(AddTeacherToLicense, self).get_context_data(**kwargs)
        context['is_add_teacher_to_license'] = True
        return context


home = Home.as_view()
add_teacher_to_license = AddTeacherToLicense.as_view()
