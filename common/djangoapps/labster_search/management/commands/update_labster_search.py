from django.core.management.base import BaseCommand

from labster_search.models import update_all_lab_keywords, update_lab_keywords_from_courses


class Command(BaseCommand):

    def handle(self, *args, **options):
        update_lab_keywords_from_courses()
        update_all_lab_keywords()
