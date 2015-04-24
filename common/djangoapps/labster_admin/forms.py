from django import forms
from django.contrib.auth.models import User
from django.forms.widgets import CheckboxSelectMultiple

from student.models import CourseEnrollment, UserProfile, CourseAccessRole
from student.roles import CourseStaffRole, CourseInstructorRole

from labster.models import LabsterCourseLicense, LabsterUser, Lab
from labster.tasks import duplicate_courses


class TeacherToLicenseForm(forms.Form):

    user_id = forms.IntegerField(label='User ID')
    license_id = forms.IntegerField(label='License ID')

    def __init__(self, *args, **kwargs):
        super(TeacherToLicenseForm, self).__init__(*args, **kwargs)
        self.fields['user_id'].widget.attrs = {'class': "form-control"}
        self.fields['license_id'].widget.attrs = {'class': "form-control"}

    def clean_user_id(self):
        user_id = self.cleaned_data.get('user_id')
        if user_id:
            try:
                User.objects.get(id=user_id)
            except User.DoesNotExist:
                raise forms.ValidationError('Invalid User ID')
        return user_id

    def clean_license_id(self):
        license_id = self.cleaned_data.get('license_id')
        if license_id:
            if not LabsterCourseLicense.objects.filter(license_id=license_id).exists():
                raise forms.ValidationError('Invalid License ID')
        return license_id

    def save(self, *args, **kwargs):
        user_id = self.cleaned_data.get('user_id')
        user = User.objects.get(id=user_id)

        license_id = self.cleaned_data.get('license_id')
        licenses = LabsterCourseLicense.objects.filter(license_id=license_id)
        course_ids = []

        for license in licenses:
            CourseInstructorRole(license.course_id).add_users(user)
            CourseStaffRole(license.course_id).add_users(user)
            CourseEnrollment.objects.get_or_create(
                user=user, course_id=license.course_id)

            course_ids.append(license.course_id)

        return user, course_ids

IS_VOUCHER_CHOICES = ((True, 'Yes',), (False, 'No',))

class DuplicateMultipleCourseForm(forms.Form):

    email = forms.EmailField()
    license_count = forms.IntegerField(required=True)
    org = forms.CharField(required=True, label='University Name')
    all_labs = forms.BooleanField(required=False, help_text='Choose this to duplicate all courses')
    labs = forms.MultipleChoiceField(required=False, widget=CheckboxSelectMultiple, choices=[])
    is_voucher = forms.ChoiceField(widget=forms.RadioSelect, choices=IS_VOUCHER_CHOICES, help_text="Are you using voucher code")
    voucher_code = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super(DuplicateMultipleCourseForm, self).__init__(*args, **kwargs)
        labs_choices = tuple([(lab.demo_course_id, lab.name) for lab in Lab.objects.all() if lab.demo_course_id])
        self.fields['labs'].choices = labs_choices
        self.fields['is_voucher'].initial = True
        self.fields['is_voucher'].widget.attrs = {'class': "form-control is_voucher"}
        self.fields['email'].widget.attrs = {'class': "form-control"}
        self.fields['license_count'].widget.attrs = {'class': "form-control"}
        self.fields['org'].widget.attrs = {'class': "form-control"}
        self.fields['voucher_code'].widget.attrs = {'class': "form-control"}

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            try:
                LabsterUser.objects.get(user__email=email)
            except User.DoesNotExist:
                raise forms.ValidationError('Invalid User Email')
        return email

    def clean_labs(self):
        labs = self.cleaned_data.get('labs')
        all_labs = self.cleaned_data.get('all_labs')

        if not labs and not all_labs:
            raise forms.ValidationError('Please select minimum one lab')

        return labs

    def save(self, *args, **kwargs):
        request = kwargs.get('request')
        email = self.cleaned_data.get('email')
        labs = self.cleaned_data.get('labs')
        all_labs = self.cleaned_data.get('all_labs')
        license_count = self.cleaned_data.get('license_count')
        org = self.cleaned_data.get('org')

        user = User.objects.get(email=email)

        duplicate_courses.delay(user.id, license_count, all_labs, labs, org, request_user_id=request.user.id)

        return user
