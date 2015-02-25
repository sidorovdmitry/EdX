from django.db import models

from django.utils import timezone


class Organization(models.Model):
    name = models.CharField(max_length=255, db_index=True)

    created_at = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        return self.name
