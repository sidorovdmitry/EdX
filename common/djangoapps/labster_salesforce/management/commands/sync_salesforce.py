from django.core.management.base import BaseCommand

from labster_accounts.organizations import get_organization
from labster_salesforce.models import Account
from labster_salesforce.salesforce import list_accounts


class Command(BaseCommand):

    def sync_accounts(self):
        """
        Sync account from salesforce to labster_acccounts.models.Organization
        """
        accounts = list_accounts()
        for account_id, name in accounts:
            # check for row in Account model
            try:
                account = Account.objects.get(account_id=account_id)
            except Account.DoesNotExist:
                account = Account()
                account.account_id = account_id
                account.organization = get_organization(name)
                account.save()

    def handle(self, *args, **options):
        self.sync_accounts()
