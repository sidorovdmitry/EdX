from django.db import models
from django.utils import timezone

from xmodule_django.models import CourseKeyField


class DemoCourse(models.Model):

    course_id = CourseKeyField(max_length=255, db_index=True, unique=True)
    url_path = models.CharField(max_length=255, blank=True, default="")

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(default=timezone.now)

    def get_url_path(self):
        if self.url_path:
            if not self.url_path.startswith('/'):
                self.url_path = '/{}'.format(self.url_path)
            if not self.url_path.endswith('/'):
                self.url_path = '{}/'.format(self.url_path)
        return self.url_path

    def save(self, *args, **kwargs):
        self.url_path = self.get_url_path()
        self.modified_at = timezone.now()
        if not self.url_path:
            self.is_active = False
        return super(DemoCourse, self).save(*args, **kwargs)
