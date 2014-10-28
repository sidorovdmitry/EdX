from django import forms
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView

from labster.edx_bridge import duplicate_lab_content, duplicate_course
from labster.models import Lab


def duplicate_lab(request):
    redirect_url = request.POST.get('redirect_url')

    if request.method != 'POST':
        return redirect(redirect_url)

    parent_locator = request.POST.get('parent_locator')
    source_locator = request.POST.get('source_locator')

    if not all([parent_locator, source_locator, redirect_url]):
        return redirect(redirect_url)

    duplicate_lab_content(request.user, source_locator, parent_locator)
    return redirect(redirect_url)


class CourseDuplicateForm(forms.Form):
    source = forms.CharField(help_text="course id in slash format, e.g. LabsterX/CYT101/2014")
    target = forms.CharField(help_text="course id in slash format, e.g. LabsterX/NEW-CYT101/2014")

    def duplicate(self, user):
        source = self.cleaned_data.get('source')
        target = self.cleaned_data.get('target')

        course = duplicate_course(source, target, user)

        return course


def allowed_to_duplicate(user):
    return user.is_authenticated() and user.is_staff and user.is_superuser


class CourseDuplicate(FormView):
    form_class = CourseDuplicateForm
    template_name = "labster/cms/duplicate_course.html"

    def dispatch(self, request, *args, **kwargs):
        if not allowed_to_duplicate(request.user):
            return HttpResponseForbidden()
        return super(CourseDuplicate, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.course = form.duplicate(self.request.user)
        return super(CourseDuplicate, self).form_valid(form)

    def get_success_url(self):
        url = '/course/{}'.format(self.course.id)
        return url



class ManageLab(TemplateView):
    template_name = "labster/cms/manage_lab.html"

    def get_context_data(self, **kwargs):
        context = super(ManageLab, self).get_context_data(**kwargs)

        labs = Lab.fetch_with_lab_proxies()

        context.update({
            'labs': labs,
        })

        return context


duplicate_course_view = CourseDuplicate.as_view()
manage_lab_view = ManageLab.as_view()
