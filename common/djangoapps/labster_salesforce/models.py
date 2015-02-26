from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from labster_accounts.models import Organization


class Lead(models.Model):
    user = models.ForeignKey(User)
    lead_id = models.CharField(max_length=100, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        return self.lead_id


class Account(models.Model):
    organization = models.ForeignKey(Organization)
    account_id = models.CharField(max_length=100, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        return self.account_id


class Contact(models.Model):
    user = models.ForeignKey(User)
    contact_id = models.CharField(max_length=100, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        return self.contact_id
