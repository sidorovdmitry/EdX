from django.core.management.base import BaseCommand, CommandError
from util.cache import cache


def flush_cache(keyspace):
    if cache.get(keyspace):
        cache.delete(keyspace)


class Command(BaseCommand):
    def handle(self, *args, **options):
        for keyspace in ('labster.landing.view.index', 'labster.landing.view.courses'):
            flush_cache(keyspace)
            print 'Removed %s keyspace' % keyspace