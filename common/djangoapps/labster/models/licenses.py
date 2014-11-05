from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from xmodule_django.models import CourseKeyField, LocationKeyField


class LabsterUserLicense(models.Model):
    """
    Tracks user's licenses against course
    """
    course_id = CourseKeyField(max_length=255, db_index=True)
    user = models.ForeignKey(User)

    created_at = models.DateTimeField(default=timezone.now)
    expired_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('course_id', 'user')

    def __unicode__(self):
        return "{} - {}".format(course_id, user)

    @property
    def is_expired(self):
        return self.expired_at and timezone.now() > self.expired_at

    def renew_to(self, expired_at):
        self.expired_at = expired_at
        self.save()
