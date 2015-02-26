from labster_accounts.models import Organization


def get_or_create_organization(name):
    label = name
    name = name.strip().lower()
    try:
        org = Organization.objects.get(name=name)
    except Organization.DoesNotExist:
        org = Organization.objects.create(name=name, label=label)
    return org
