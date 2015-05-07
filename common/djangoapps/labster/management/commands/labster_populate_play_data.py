from django.core.management.base import BaseCommand

from labster.models import Lab
from labster.reports import get_play_count, get_duration


class Command(BaseCommand):

    def handle(self, *args, **options):
        labs = Lab.objects.all()
        for lab in labs:
            self.stdout.write(lab.name)
            play_count = get_play_count(lab)
            duration = get_duration(lab)
            Lab.objects.filter(id=lab.id).update(play_count=play_count, duration=duration)
            self.stdout.write(", play count: {}, duration: {}\n".format(play_count, duration))
