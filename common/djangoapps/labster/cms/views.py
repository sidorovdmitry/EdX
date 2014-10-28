import json

from django import forms
from django.http import HttpResponseForbidden, Http404, HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_protect
from django.views.generic import FormView, TemplateView, View

from labster.edx_bridge import duplicate_lab_content, duplicate_course
from labster.quiz_blocks import update_lab_quiz_block, update_master_lab
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
        assert self.request.user.is_authenticated() and self.request.user.is_superuser
        context = super(ManageLab, self).get_context_data(**kwargs)

        labs = Lab.fetch_with_lab_proxies()
        context.update({
            'labs': labs,
        })

        return context


class UpdateQuizBlock(View):

    def post(self, request, *args, **kwargs):
        assert self.request.user.is_authenticated() and self.request.user.is_superuser
        lab_id = kwargs.get('lab_id')
        try:
            lab = Lab.objects.get(id=lab_id)
        except Lab.DoesNotExist:
            raise Http404

        update_lab_quiz_block(lab, request.user)
        update_master_lab(lab, request.user, force_update=True)
        lab = Lab.objects.get(id=lab_id)

        response = {
            'quiz_block_last_updated': lab.quiz_block_last_updated.isoformat(),
        }
        response = json.dumps(response)
        return HttpResponse(response, content_type='application/json')


duplicate_course_view = CourseDuplicate.as_view()
manage_lab_view = csrf_protect(ManageLab.as_view())
update_quiz_block_view = UpdateQuizBlock.as_view()
