from django import forms
from django.contrib import admin
from django.contrib.auth.models import User

from student.models import UserProfile

from labster.models import LabsterUser
from labster.user_utils import generate_unique_username


class LabsterUserForm(forms.ModelForm):

    name = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(required=False, widget=forms.PasswordInput)
    user_is_active = forms.BooleanField(
        required=False,
        help_text="False means user can't login")

    gender = forms.ChoiceField(choices=UserProfile.GENDER_CHOICES, required=False)
    level_of_education = forms.ChoiceField(choices=UserProfile.LEVEL_OF_EDUCATION_CHOICES, required=False)

    class Meta:
        model = LabsterUser
        exclude = ('user', 'ip_address')

    def __init__(self, *args, **kwargs):
        super(LabsterUserForm, self).__init__(*args, **kwargs)
        self.fields['is_active'].help_text = "False means user can't play lab"

        if self.instance.id:
            user = self.instance.user
            user_profile = UserProfile.objects.get(user=user)
            self.fields['email'].initial = user.email
            self.fields['user_is_active'].initial = user.is_active
            self.fields['name'].initial = user_profile.name
            self.fields['gender'].initial = user_profile.gender
            self.fields['level_of_education'].initial = user_profile.level_of_education
            self.fields['is_active'].initial = self.instance.is_active
            self.fields['user_type'].initial = self.instance.user_type
            self.fields['user_school_level'].initial = self.instance.user_school_level
            self.fields['phone_number'].initial = self.instance.phone_number
            self.fields['organization_name'].initial = self.instance.organization_name
            self.fields['nationality'].initial = self.instance.nationality
            self.fields['unique_id'].initial = self.instance.unique_id
            self.fields['language'].initial = self.instance.language
            self.fields['date_of_birth'].initial = self.instance.date_of_birth

            self.fields['password'].widget.attrs['disabled'] = True

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
        name = data.get('name')

        if self.instance.id:
            user = self.instance.user
        else:
            user = User()
            user.username = generate_unique_username(name, User)

        user.email = data.get('email')
        user.is_active = data.get('user_is_active', False)
        password = data.get('password')
        if not user.id:
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


def make_active(modeladmin, request, queryset):
    queryset.update(is_active= True)
make_active.short_description = "Set active"

def make_inactive(modeladmin, request, queryset):
    queryset.update(is_active= False)
make_inactive.short_description = "Set inactive"


class LabsterUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'user_id', 'username', 'user_type_display', 'is_active', 'ip_address')
    search_fields = ('user__email', 'user__username',)
    list_filter = ('user__is_active', 'user_type', 'is_new')
    raw_id_fields = ('user',)
    actions = (make_active, make_inactive)
    fieldsets = (
        (None, {'fields': (
            # 'user',
            'email',
            'password',
            'user_is_active',
        )}),
        (None, {
            'fields': (
                'name',
                'is_active',
                'is_email_active',
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
