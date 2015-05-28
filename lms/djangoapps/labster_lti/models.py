from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from labster_lti.utils import create_user


class LTIUser(models.Model):
    user = models.ForeignKey(User)
    external_user_id = models.CharField(max_length=100)
    provider = models.CharField(max_length=100)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('external_user_id', 'provider')

    @classmethod
    def create(cls, external_user_id, provider):
        try:
            obj = cls.objects.get(external_user_id=external_user_id, provider__iexact=provider.strip())
        except cls.DoesNotExist:
            obj = cls(external_user_id=external_user_id, provider=provider.strip())
            obj.user = create_user(external_user_id, provider)
            obj.save()
        return obj
