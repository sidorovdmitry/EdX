import hashlib

from django.contrib.auth.models import User
from django.utils import timezone

from rest_framework import serializers


def get_username(email, length=10):
    string = "{}{}".format(email, timezone.now().isoformat())
    return hashlib.sha1(string).hexdigest()[:length]


class UserCreateSerializer(serializers.Serializer):

    id = serializers.Field()
    email = serializers.EmailField()

    def validate_email(self, attrs, source):
        value = attrs[source]
        if value and User.objects.filter(email__iexact=value.strip()).exists():
            raise serializers.ValidationError("Email is used")

        return attrs

    def save_object(self, *args, **kwargs):
        self.object.username = get_username(self.object.email)
        self.object.set_unusable_password()
        self.object.save()

        return self.object

    def restore_object(self, attrs, instance=None):
        if instance:
            instance.email = attrs.get('email', instance.email)
            return instance

        return User(**attrs)


class CustomLabsterUser(object):

    def __init__(self, *args, **kwargs):
        for field in kwargs.keys():
            setattr(self, field, kwargs.get(field))

    def save(self):
        user = User.objects.get(id=self.id)
        labster_user = user.labster_user
        labster_user.nationality = self.nationality
        labster_user.language = self.language
        labster_user.unique_id = self.unique_id
        labster_user.date_of_birth = self.date_of_birth
        labster_user.save()
        return user


class LabsterUserSerializer(serializers.Serializer):

    user_id = serializers.Field()
    is_labster_verified = serializers.Field()
    nationality_name = serializers.Field()

    date_of_birth = serializers.DateField()
    nationality = serializers.CharField()
    language = serializers.CharField()
    unique_id = serializers.CharField()

    def save_object(self, *args, **kwargs):
        self.object.save()
        return self.object

    def restore_object(self, attrs, instance=None):
        if instance:
            instance.unique_id = attrs.get('unique_id', instance.unique_id)
            instance.nationality = attrs.get('nationality', instance.nationality)
            instance.language = attrs.get('language', instance.language)
            instance.date_of_birth = attrs.get('date_of_birth', instance.date_of_birth)
            return instance

        return CustomLabsterUser(**attrs)
