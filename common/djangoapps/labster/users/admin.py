from django import forms
from django.contrib import admin
from django.contrib.auth.models import User

from student.models import UserProfile

from labster.models import LabsterUser
from labster.user_utils import generate_unique_username


class LabsterUserForm(forms.ModelForm):

    name = forms.CharField()
    email = forms.EmailField()
    is_active = forms.BooleanField(required=False)
    password = forms.CharField(required=False, widget=forms.PasswordInput)

    gender = forms.ChoiceField(choices=UserProfile.GENDER_CHOICES, required=False)
    level_of_education = forms.ChoiceField(choices=UserProfile.LEVEL_OF_EDUCATION_CHOICES, required=False)

    class Meta:
        model = LabsterUser
        exclude = ('user',)

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if email:
            users = User.objects.filter(email__iexact=email)
            if self.instance.id:
                users = users.exclude(id=self.instance.user.id)

            if users.exists():
                raise forms.ValidationError('Email is used')

        return email

    def get_or_create_user(self, data):
        if self.instance.id:
            user = self.instance.user
        else:
            user = User()

        user.email = data.get('email')

        name = data.get('name')
        user.username = generate_unique_username(name, User)
        user.is_active = data.get('is_active', False)

        password = data.get('password')
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()

        self.get_or_create_user_profile(user=user, data=data)

        return user

    def get_or_create_user_profile(self, user, data):
        try:
            user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            user_profile = UserProfile(user=user)

        user_profile.name = data.get('name')
        user_profile.gender = data.get('gender', '')
        user_profile.level_of_education = data.get('level_of_education', '')
        user_profile.save()

        return user_profile

    def save(self, *args, **kwargs):
        data = self.cleaned_data
        kwargs['commit'] = False
        labster_user = super(LabsterUserForm, self).save(*args, **kwargs)

        user = self.get_or_create_user(data)

        labster_user.id = user.labster_user.id
        labster_user.user = user
        labster_user.save()

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
                'organization_name',
                'user_school_level',
                'phone_number',
                'date_of_birth',
                'language',
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
