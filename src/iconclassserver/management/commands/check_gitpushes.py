from django.core.management.base import BaseCommand
from iconclassserver.util import handle_githubpushes

class Command(BaseCommand):
    help = 'Checks the REDIS queue for Git pushes and applies them'

    def handle(self, *args, **options):
        handle_githubpushes()