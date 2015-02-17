from django import forms
from django.contrib import admin
from django.contrib.auth.models import User

from student.models import UserProfile

from labster.models import LabsterUser


class LabsterUserForm(forms.ModelForm):

    name = forms.CharField(max_length=255, required=False)
    email = forms.EmailField(max_length=255)
    is_active = forms.BooleanField(required=False)

    gender = forms.ChoiceField(choices=UserProfile.GENDER_CHOICES, required=False)
    level_of_education = forms.ChoiceField(choices=UserProfile.LEVEL_OF_EDUCATION_CHOICES, required=False)

    class Meta:
        model = LabsterUser

    def clean_email(self,

    def save(self, *args, **kwargs):
        data = self.cleaned_data
        kwargs['commit'] = False
        labster_user = super(LabsterUserForm, self).save(*args, **kwargs)

        return labster_user


class LabsterUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'user_id', 'username', 'user_type_display')
    search_fields = ('user__email', 'user__first_name', 'user__last_name',)
    list_filter = ('user__is_active', 'user_type',)
    raw_id_fields = ('user',)
    fieldsets = (
        (None, {'fields': (
            # 'user',
            'email',
            'is_active',
        )}),
        (None, {
            'fields': (
                'name',
                'gender',
                'level_of_education',
            )
        }),
        (None, {
            'fields': (
                'user_type',
                'phone_number',
                'organization_name',
                'user_school_level',
                'language',
                'date_of_birth',
                'nationality',
                'unique_id',
            )
        }),
    )
    form = LabsterUserForm

    def email(self, obj):
        return obj.user.email

    def user_id(self, obj):
        return obj.user.id

    def username(self, obj):
        return obj.user.username

    def user_type_display(self, obj):
        return obj.get_user_type_display()


