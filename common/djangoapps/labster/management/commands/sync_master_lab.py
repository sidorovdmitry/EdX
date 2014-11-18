from django.core.management.base import BaseCommand

from labster.models import Lab
from labster.masters import fetch_quizblocks


class Command(BaseCommand):

    def handle(self, *args, **options):

        labs = Lab.objects.order_by('id')
        total = labs.count()

        for index, lab in enumerate(labs, start=1):
            self.stdout.write("{}/{}: {}\n".format(
                index, total, lab.name))

            fetch_quizblocks(lab)
