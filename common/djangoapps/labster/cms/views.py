import json

from django import forms
from django.http import HttpResponseForbidden, Http404, HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_protect
from django.views.generic import FormView, TemplateView, View

from labster.courses import duplicate_course
from labster.edx_bridge import duplicate_lab_content
from labster.masters import fetch_quizblocks
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

    def duplicate(self, user, http_protocol):
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
        absolute_uri = self.request.build_absolute_uri()
        http_protocol = 'https' if absolute_uri.startswith('https') else 'http'
        self.course = form.duplicate(self.request.user, http_protocol)
        return super(CourseDuplicate, self).form_valid(form)

    def get_success_url(self):
        url = '/course/{}'.format(self.course.id)
        return url


class AdminOnlyMixin(object):

    def dispatch(self, request, *args, **kwargs):
        allowed = [request.user.is_authenticated(),
                   request.user.is_superuser]

        if not all(allowed):
            return HttpResponseForbidden()

        return super(AdminOnlyMixin, self).dispatch(request, *args, **kwargs)


class ManageLab(AdminOnlyMixin, TemplateView):
    template_name = "labster/cms/manage_lab.html"

    def get_context_data(self, **kwargs):
        assert self.request.user.is_authenticated() and self.request.user.is_superuser
        context = super(ManageLab, self).get_context_data(**kwargs)

        labs = Lab.fetch_with_lab_proxies()
        context.update({
            'labs': labs,
        })

        return context


class UpdateQuizBlock(AdminOnlyMixin, View):

    def post(self, request, *args, **kwargs):
        assert self.request.user.is_authenticated() and self.request.user.is_superuser
        lab_id = kwargs.get('lab_id')
        try:
            lab = Lab.objects.get(id=lab_id)
        except Lab.DoesNotExist:
            raise Http404

        fetch_quizblocks(lab)
        lab = Lab.objects.get(id=lab_id)

        response = {
            'quiz_block_last_updated': lab.quiz_block_last_updated.isoformat(),
        }
        response = json.dumps(response)
        return HttpResponse(response, content_type='application/json')


duplicate_course_view = CourseDuplicate.as_view()
manage_lab_view = csrf_protect(ManageLab.as_view())
update_quiz_block_view = UpdateQuizBlock.as_view()
