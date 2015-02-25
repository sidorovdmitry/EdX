from django.db import models
from django.contrib.auth.models import User

from labster_accounts.models import Organization


class Lead(models.Model):
    user = models.OneToOneField(User)
    lead_id = models.CharField(max_length=100, db_index=True)

    def __unicode__(self):
        return self.lead_id


class Account(models.Model):
    organization = models.OneToOneField(Organization)
    account_id = models.CharField(max_length=100, db_index=True)

    def __unicode__(self):
        return self.account_id


class Contact(models.Model):
    user = models.OneToOneField(User)
    contact_id = models.CharField(max_length=100, db_index=True)

    def __unicode__(self):
        return self.contact_id
