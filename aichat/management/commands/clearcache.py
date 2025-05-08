from django.core.management.base import BaseCommand
from django.core.cache import caches

class Command(BaseCommand):
    help = 'Clearcache'

    def handle(self, *args, **kwargs):
        for cache_name in caches:
            caches[cache_name].clear()
        self.stdout.write('Cache cleared successfully!')