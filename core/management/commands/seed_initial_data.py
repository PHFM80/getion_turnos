from django.core.management.base import BaseCommand
from django.db import transaction

from core.seed import seed_initial_data


class Command(BaseCommand):
    help = 'Carga datos base (geo, rubros, servicios).'

    @transaction.atomic
    def handle(self, *args, **options):
        seed_initial_data()

        self.stdout.write(self.style.SUCCESS('Datos base cargados.'))
