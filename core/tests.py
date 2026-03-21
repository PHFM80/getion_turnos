from datetime import date, timedelta
from uuid import uuid4

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from agenda.models import BloqueoEmpresa, CapacidadEmpresa, CapacidadPuesto, HorarioEmpresa
from core.models import Usuario
from core.views import sync_estado_suscripcion
from empresas.models import Empresa, Rubro
from geo.models import Localidad, Pais, Provincia
from servicios.models import ServicioBase, ServicioEmpresa
from suscripciones.models import Plan, Suscripcion


class AdminEmpresaConfiguracionTests(TestCase):
    def setUp(self):
        self.admin = Usuario.objects.create_user(
            email="admin@test.com",
            password="admin123",
            nombre="Admin",
            apellido="Test",
            dni="11111111",
            telefono="1111111111",
            is_staff=True,
            is_superuser=True,
        )

        suffix = uuid4().hex[:8]
        self.pais = Pais.objects.create(nombre=f"Argentina {suffix}", codigo="54")
        self.provincia = Provincia.objects.create(nombre=f"Buenos Aires {suffix}", pais=self.pais)
        self.localidad = Localidad.objects.create(nombre=f"La Plata {suffix}", provincia=self.provincia)
        self.rubro = Rubro.objects.create(nombre=f"Peluqueria {suffix}")

        self.empresa = Empresa.objects.create(
            nombre="Pascual Porco Estilistas",
            telefono="+541122223333",
            calle="Calle 1",
            numero="123",
            activo=True,
            pais=self.pais,
            provincia=self.provincia,
            localidad=self.localidad,
            rubro=self.rubro,
        )

        self.plan = Plan.objects.create(
            nombre="Plan 2",
            limite_simultaneo=2,
            precio_mensual=1000,
            precio_anual=10000,
        )

        self.suscripcion = Suscripcion.objects.create(
            empresa=self.empresa,
            plan=self.plan,
            activa=True,
            periodicidad=Suscripcion.PERIODO_MENSUAL,
            fecha_inicio=timezone.now().date() - timedelta(days=10),
            fecha_vencimiento=timezone.now().date() + timedelta(days=20),
        )

        self.client.force_login(self.admin)
        self.url = reverse("dashboard_admin_empresa_editar", args=[self.empresa.id])

    def test_admin_puede_agregar_servicio_empresa_desde_edicion(self):
        servicio_base = ServicioBase.objects.create(nombre="Corte", rubro=self.rubro)

        response = self.client.post(
            self.url,
            {
                "form_type": "servicio_empresa",
                "servicio_base": servicio_base.id,
                "duracion_minutos": 45,
                "precio": "12000",
                "activo": "on",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        servicio = ServicioEmpresa.objects.get(empresa=self.empresa, servicio_base=servicio_base)
        self.assertEqual(servicio.precio, 12000)
        self.assertEqual(servicio.duracion.total_seconds(), 45 * 60)
        self.assertTrue(servicio.activo)

    def test_capacidad_no_puede_superar_limite_del_plan(self):
        response = self.client.post(
            self.url,
            {
                "form_type": "capacidad",
                "capacidad": 3,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "no puede superar el limite del plan")
        self.assertFalse(CapacidadEmpresa.objects.filter(empresa=self.empresa).exists())

    def test_capacidad_crea_puestos_y_permite_nombres_parciales(self):
        self.plan.limite_simultaneo = 4
        self.plan.save(update_fields=["limite_simultaneo"])

        response_capacidad = self.client.post(
            self.url,
            {
                "form_type": "capacidad",
                "capacidad": 4,
            },
            follow=True,
        )
        self.assertEqual(response_capacidad.status_code, 200)

        capacidad = CapacidadEmpresa.objects.get(empresa=self.empresa)
        puestos = list(CapacidadPuesto.objects.filter(capacidad=capacidad).order_by("orden"))
        self.assertEqual(len(puestos), 4)

        response_nombres = self.client.post(
            self.url,
            {
                "form_type": "capacidad_nombres",
                "puestos_nombres": ["Peluquero 1", "Peluquero 2", "Peluquero 3", ""],
            },
            follow=True,
        )
        self.assertEqual(response_nombres.status_code, 200)

        puestos = list(CapacidadPuesto.objects.filter(capacidad=capacidad).order_by("orden"))
        self.assertEqual(puestos[0].nombre, "Peluquero 1")
        self.assertEqual(puestos[1].nombre, "Peluquero 2")
        self.assertEqual(puestos[2].nombre, "Peluquero 3")
        self.assertIsNone(puestos[3].nombre)

    def test_admin_puede_agregar_horario_y_bloqueo_desde_edicion(self):
        response_horario = self.client.post(
            self.url,
            {
                "form_type": "horario",
                "dia_semana": 0,
                "hora_inicio": "09:00",
                "hora_fin": "13:00",
            },
            follow=True,
        )
        self.assertEqual(response_horario.status_code, 200)
        self.assertTrue(
            HorarioEmpresa.objects.filter(
                empresa=self.empresa,
                dia_semana=0,
                hora_inicio="09:00",
                hora_fin="13:00",
            ).exists()
        )

        response_bloqueo = self.client.post(
            self.url,
            {
                "form_type": "bloqueo",
                "fecha": "2026-04-10",
                "hora_inicio": "10:00",
                "hora_fin": "12:00",
                "motivo": "Mantenimiento",
            },
            follow=True,
        )
        self.assertEqual(response_bloqueo.status_code, 200)
        self.assertTrue(
            BloqueoEmpresa.objects.filter(
                empresa=self.empresa,
                fecha=date(2026, 4, 10),
                motivo="Mantenimiento",
            ).exists()
        )

    def test_expiracion_suscripcion_crea_bloqueo_automatico(self):
        hoy = timezone.now().date()
        self.suscripcion.fecha_vencimiento = hoy - timedelta(days=1)
        self.suscripcion.activa = True
        self.suscripcion.save(update_fields=["fecha_vencimiento", "activa"])

        sync_estado_suscripcion(self.suscripcion, today=hoy)
        self.suscripcion.refresh_from_db()

        self.assertFalse(self.suscripcion.activa)
        self.assertTrue(
            BloqueoEmpresa.objects.filter(
                empresa=self.empresa,
                fecha=hoy,
                motivo="Bloqueo automatico por falta de pago",
            ).exists()
        )
