from labster_accounts.organizations import get_or_create_organization
from labster_salesforce.models import Account


def get_or_create_account(account_id, name):
    try:
        account = Account.objects.get(account_id=account_id)
    except Account.DoesNotExist:
        account = Account()
        account.account_id = account_id
        account.organization = get_or_create_organization(name)
        account.save()

    return account
