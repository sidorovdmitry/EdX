from django import forms
from django.contrib.auth.models import User

from student.models import CourseEnrollment
from student.roles import CourseStaffRole, CourseInstructorRole

from labster.models import LabsterCourseLicense


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
