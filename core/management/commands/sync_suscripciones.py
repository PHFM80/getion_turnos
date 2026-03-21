from django.core.management.base import BaseCommand
from django.utils import timezone

from suscripciones.models import Suscripcion


class Command(BaseCommand):
    help = "Sincroniza estado de suscripciones: desactiva las vencidas."

    def add_arguments(self, parser):
        parser.add_argument(
            "--quiet",
            action="store_true",
            help="No imprime detalle por consola, solo errores.",
        )

    def handle(self, *args, **options):
        quiet = options["quiet"]
        today = timezone.now().date()

        vencidas_qs = Suscripcion.objects.filter(
            activa=True,
            fecha_vencimiento__isnull=False,
            fecha_vencimiento__lt=today,
        )

        total_vencidas = vencidas_qs.count()
        updated = vencidas_qs.update(activa=False)

        if not quiet:
            self.stdout.write(
                self.style.SUCCESS(
                    f"[sync_suscripciones] Fecha: {today} | "
                    f"Vencidas detectadas: {total_vencidas} | "
                    f"Desactivadas: {updated}"
                )
            )
