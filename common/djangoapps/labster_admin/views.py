from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, FormView

from labster_admin.forms import TeacherToLicenseForm, DuplicateMultipleCourseForm


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


class DuplicateMultipleCourse(StaffMixin, FormView):
    template_name = "labster_admin/duplicate_multiple_courses.html"
    form_class = DuplicateMultipleCourseForm

    def get_success_url(self):
        return reverse('labster_duplicate_multiple_courses')

    def form_valid(self, form):
        user = form.save()
        messages.success(
            self.request,
            "<strong>{}</strong> banana".format(user))

        return super(DuplicateMultipleCourse, self).form_valid(form)


home = Home.as_view()
add_teacher_to_license = AddTeacherToLicense.as_view()
duplicate_multiple_courses = DuplicateMultipleCourse.as_view()
