from django.contrib.auth.models import User
from django.http import Http404

from rest_framework import generics

from labster.api.users.serializers import UserCreateSerializer, LabsterUserSerializer
from labster.api.views import AuthMixin
from labster.models import LabsterUser


class UserCreate(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    model = User


class UserView(AuthMixin, generics.RetrieveUpdateAPIView):

    serializer_class = LabsterUserSerializer

    def get_object(self):
        try:
            return self.get_queryset().get(user__id=self.kwargs.get('user_id'))
        except LabsterUser.DoesNotExist:
            raise Http404

    def get_queryset(self):
        return LabsterUser.objects.all()
