from labster_salesforce.models import Lead


def get_or_create_lead(lead_id, user):
    try:
        lead = Lead.objects.get(lead_id=lead_id)
    except Lead.DoesNotExist:
        lead = Lead()
        lead.lead_id = lead_id
        lead.user = user
        lead.save()

    return lead
