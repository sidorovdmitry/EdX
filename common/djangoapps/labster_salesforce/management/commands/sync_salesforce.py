from django.core.management.base import BaseCommand

from labster_salesforce.salesforce import list_accounts
from labster_salesforce.accounts import get_or_create_account


class Command(BaseCommand):

    def sync_accounts(self):
        """
        Sync account from salesforce to labster_acccounts.models.Organization
        """
        accounts = list_accounts()
        for account_id, name in accounts:
            get_or_create_account(account_id, name)

    def handle(self, *args, **options):
        self.sync_accounts()
