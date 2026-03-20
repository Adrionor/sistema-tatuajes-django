from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from citas.models import Cita
from cotizaciones.emails import correo_recordatorio


class Command(BaseCommand):
    help = "Envía recordatorios por correo a clientes y tatuadores (7 días y 1 día antes)."

    def handle(self, *args, **options):
        ahora = timezone.now()
        enviados = 0
        errores = 0

        # ---------- 7 DÍAS ANTES ----------
        objetivo_7 = ahora + timedelta(days=7)
        ventana_ini_7 = objetivo_7.replace(hour=0, minute=0, second=0, microsecond=0)
        ventana_fin_7 = ventana_ini_7 + timedelta(days=1)

        citas_7 = Cita.objects.filter(
            estado='programada',
            recordatorio_semana_enviado=False,
            fecha_hora_inicio__gte=ventana_ini_7,
            fecha_hora_inicio__lt=ventana_fin_7,
        )

        for cita in citas_7:
            try:
                correo_recordatorio(cita, dias_antes=7)
                cita.recordatorio_semana_enviado = True
                cita.save(update_fields=['recordatorio_semana_enviado'])
                enviados += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"[7 días] Recordatorio enviado: {cita.cotizacion.nombre_cliente} — {cita.fecha_hora_inicio:%d/%m/%Y %H:%M}"
                    )
                )
            except Exception as exc:
                errores += 1
                self.stderr.write(f"[7 días] Error en cita {cita.id}: {exc}")

        # ---------- 1 DÍA ANTES ----------
        objetivo_1 = ahora + timedelta(days=1)
        ventana_ini_1 = objetivo_1.replace(hour=0, minute=0, second=0, microsecond=0)
        ventana_fin_1 = ventana_ini_1 + timedelta(days=1)

        citas_1 = Cita.objects.filter(
            estado='programada',
            recordatorio_dia_enviado=False,
            fecha_hora_inicio__gte=ventana_ini_1,
            fecha_hora_inicio__lt=ventana_fin_1,
        )

        for cita in citas_1:
            try:
                correo_recordatorio(cita, dias_antes=1)
                cita.recordatorio_dia_enviado = True
                cita.save(update_fields=['recordatorio_dia_enviado'])
                enviados += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"[1 día]  Recordatorio enviado: {cita.cotizacion.nombre_cliente} — {cita.fecha_hora_inicio:%d/%m/%Y %H:%M}"
                    )
                )
            except Exception as exc:
                errores += 1
                self.stderr.write(f"[1 día] Error en cita {cita.id}: {exc}")

        self.stdout.write(
            self.style.SUCCESS(f"\nListo — {enviados} recordatorio(s) enviado(s), {errores} error(es).")
        )
