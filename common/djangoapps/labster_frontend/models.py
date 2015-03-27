import re

from django.db import models
from django.utils import timezone

from xmodule_django.models import CourseKeyField

from labster.models import Lab


class DemoCourse(models.Model):

    course_id = CourseKeyField(max_length=255, db_index=True, unique=True)
    slug = models.CharField(max_length=255, db_index=True, blank=True, default="")
    lab = models.ForeignKey(Lab, blank=True, null=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(default=timezone.now)

    def get_slug(self):
        if not self.slug and self.lab:
            self.slug = re.sub('\s+', '-', self.lab.name)
        return self.slug

    def save(self, *args, **kwargs):
        self.slug = self.get_slug()
        self.modified_at = timezone.now()
        self.is_active = len(self.slug) > 0
        return super(DemoCourse, self).save(*args, **kwargs)
