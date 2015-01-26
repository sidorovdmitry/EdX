from django.core.management.base import BaseCommand

from labster_search.models import update_all_lab_keywords


class Command(BaseCommand):

    def handle(self, *args, **options):
        update_all_lab_keywords()
