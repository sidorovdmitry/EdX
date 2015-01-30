import hashlib

from django.contrib.auth.models import User
from django.utils import timezone

from rest_framework import serializers

from labster.models import LabsterUser


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

        return User(**attrs)


class LabsterUserSerializer(serializers.ModelSerializer):

    user_id = serializers.Field('user.id')
    is_labster_verified = serializers.Field('is_labster_verified')
    nationality_name = serializers.Field('nationality.name')

    class Meta:
        model = LabsterUser
        fields = (
            'user_id',
            'date_of_birth',
            'nationality',
            'language',
            'unique_id',
            'is_labster_verified',
            'nationality_name',
        )
