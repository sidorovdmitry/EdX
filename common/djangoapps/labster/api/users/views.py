from django.contrib.auth.models import User

from rest_framework import generics

from labster.api.users.serializers import UserCreateSerializer


class UserCreate(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    model = User
