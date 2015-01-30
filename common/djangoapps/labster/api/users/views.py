from django.contrib.auth.models import User
from django.http import Http404

from rest_framework import generics

from labster.api.users.serializers import UserCreateSerializer, LabsterUserSerializer
from labster.api.users.serializers import CustomLabsterUser
from labster.api.views import AuthMixin


def get_user_as_custom_labster_user(user):
    labster_user = user.labster_user

    return CustomLabsterUser(
        id=user.id,
        user_id=user.id,
        is_labster_verified=labster_user.is_labster_verified,
        unique_id=labster_user.unique_id,
        nationality_name=labster_user.nationality.name,
        nationality=labster_user.nationality.code,
        language=labster_user.language,
        date_of_birth=labster_user.date_of_birth,
    )


class UserCreate(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    model = User


class UserView(AuthMixin, generics.RetrieveUpdateAPIView):

    serializer_class = LabsterUserSerializer

    def get_object(self):
        try:
            user = self.get_queryset().get(id=self.kwargs.get('user_id'))
        except User.DoesNotExist:
            raise Http404

        return get_user_as_custom_labster_user(user)

    def get_queryset(self):
        return User.objects.all()
