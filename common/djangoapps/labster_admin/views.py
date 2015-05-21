from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, FormView

from labster.models import Lab
from labster_admin.forms import TeacherToLicenseForm, DuplicateMultipleCourseForm
from labster_search.forms import LabKeywordFormSet
from labster_search.models import get_primary_manual_keywords


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


class LabsPlayData(StaffMixin, TemplateView):
    template_name = "labster_admin/lab_plays_data.html"

    def get_context_data(self, **kwargs):
        context = super(LabsPlayData, self).get_context_data(**kwargs)
        context['labs'] = Lab.objects.order_by('name')
        return context


class LabKeywordsIndex(StaffMixin, TemplateView):
    template_name = "labster_admin/lab_keywords_index.html"

    def get_context_data(self, **kwargs):
        context = super(LabKeywordsIndex, self).get_context_data(**kwargs)
        context['is_labster_lab_keywords'] = True
        context['labs'] = [lab for lab in Lab.objects.order_by('name') if lab.demo_course_id]
        return context


def lab_keywords_edit(request, lab_id):
    lab = get_object_or_404(Lab, id=lab_id)
    if request.method == 'POST':
        formset = LabKeywordFormSet(
            request.POST,
            instance=lab,
        )
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(request.build_absolute_uri())
    else:
        formset = LabKeywordFormSet(
            instance=lab, queryset=get_primary_manual_keywords(lab=lab))

    context = {
        'is_labster_lab_keywords': True,
        'lab': lab,
        'formset': formset,
    }
    template_name = "labster_admin/lab_keywords_edit.html"
    return render(request, template_name, context)


home = Home.as_view()
add_teacher_to_license = AddTeacherToLicense.as_view()
duplicate_multiple_courses = DuplicateMultipleCourse.as_view()
labs_play_data = LabsPlayData.as_view()
lab_keywords_index = LabKeywordsIndex.as_view()
