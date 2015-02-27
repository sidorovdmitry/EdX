from django.conf import settings
from django.contrib.auth.models import User
from django.http import Http404
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from student.models import UserProfile

from labster.api.users.serializers import UserCreateSerializer, LabsterUserSerializer
from labster.api.users.serializers import CustomLabsterUser
from labster.api.views import AuthMixin
from labster.models import LabsterUser


def get_user_as_custom_labster_user(user, password=None):
    user = User.objects.get(id=user.id)
    labster_user = user.labster_user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    return CustomLabsterUser(
        id=user.id,
        user_id=user.id,
        is_labster_verified=labster_user.is_labster_verified,
        unique_id=labster_user.unique_id,
        nationality_name=labster_user.nationality.name,
        nationality=labster_user.nationality.code,
        language=labster_user.language,
        phone_number=labster_user.phone_number,
        user_type=labster_user.user_type,
        organization_name=labster_user.organization_name,
        user_school_level=labster_user.user_school_level,
        user_school_level_display=labster_user.get_user_school_level_display(),
        date_of_birth=labster_user.date_of_birth,
        name=profile.name,
        password=password,
        gender=profile.gender,
        year_of_birth=profile.year_of_birth,
        level_of_education=profile.level_of_education,
    )


class UserCreate(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    model = User


class SendEmailUserCreate(APIView):

    def get(self, request, *args, **kwargs):
        # Send email to Mikael everytime a teacher signs up

        try:
            user = User.objects.get(id=self.kwargs.get('user_id'))
        except User.DoesNotExist:
            raise Http404

        labster_user = get_user_as_custom_labster_user(user)

        context = {
            'user': user,
            'labster_user': labster_user,
            'user_school_level': labster_user.user_school_level_display,
        }
        email_html = render_to_string('emails/teacher_information.html', context)
        subject = "New teacher registration: {}".format(user.email)

        email = EmailMessage(subject, email_html, "no-reply@labster.com", settings.SALES_EMAIL)
        email.content_subtype = "html"
        email.send(fail_silently=False)

        http_status = status.HTTP_200_OK

        labster_user = LabsterUser.objects.get(user=user)
        if labster_user.is_new:
            from labster_salesforce.tasks import labster_create_salesforce_lead
            # labster_create_salesforce_lead.delay(instance.id)
            labster_create_salesforce_lead(user.id)

        return Response(http_status)


class UserView(AuthMixin, generics.RetrieveUpdateAPIView):

    serializer_class = LabsterUserSerializer

    def get_object(self):
        try:
            user = self.get_queryset().get(id=self.kwargs.get('user_id'))
        except User.DoesNotExist:
            raise Http404

        password = self.request.DATA.get('password')
        return get_user_as_custom_labster_user(user, password)

    def get_queryset(self):
        return User.objects.all()
