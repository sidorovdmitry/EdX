from django.core.management.base import BaseCommand

from labster_frontend.demo_courses import populate_demo_courses


class Command(BaseCommand):

    def handle(self, *args, **options):
        populate_demo_courses()
