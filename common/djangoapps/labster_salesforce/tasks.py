from celery.task import task

from django.conf import settings
from django.contrib.auth.models import User

from student.models import UserProfile

from labster.models import LabsterUser
from labster_salesforce.leads import get_or_create_lead
from labster_salesforce.salesforce import create_lead


ENABLE_SALESFORCE = settings.LABSTER_ENABLE_SALESFORCE


@task()
def labster_create_salesforce_lead(user_id):
    print 'labster_create_salesforce_lead'
    if not ENABLE_SALESFORCE:
        return

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return

    labster_user = LabsterUser.objects.get(user=user)
    if labster_user.is_lead_synced or not labster_user.is_new:
        return

    user_profile = UserProfile.objects.get(user=user)
    lead_id = create_lead(
        name=user_profile.name,
        email=user.email,
        company=labster_user.organization_name,
        occupation=labster_user.user_school_level,
        phone=labster_user.phone_number,
    )
    if lead_id:
        get_or_create_lead(lead_id, user)
        LabsterUser.objects.filter(id=labster_user.id).update(is_new=False)
