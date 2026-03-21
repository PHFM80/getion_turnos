from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.shortcuts import render
from django.db import transaction
from django.utils import timezone
from datetime import date, timedelta
from django.http import HttpResponse
import base64
from django.db.models import Count, Avg, Sum
from django.views.decorators.http import require_POST

from core.forms import (
    EmpresaCreateForm,
    EmpresaForm,
    LocalidadForm,
    PaisForm,
    PagoForm,
    PlanForm,
    ProvinciaForm,
    RubroForm,
    ServicioBaseForm,
    SuscripcionEditForm,
    SuscripcionForm,
    UsuarioEmpresaCreateForm,
    UsuarioEmpresaEditForm,
)
from core.models import UsuarioEmpresa
from empresas.models import Rubro
from empresas.models import Empresa
from geo.models import Localidad, Pais, Provincia
from servicios.models import ServicioBase
from agenda.models import Turno
from suscripciones.models import Pago, Plan, Suscripcion


def index(request):
    return render(request, 'index.html')


def servicios_publicos(request):
    empresas = [
        {"slug": "clinica-andina", "nombre": "Clínica Andina", "rubro": "Salud", "ubicacion": "Mendoza", "estado": "Activa"},
        {"slug": "autocheck", "nombre": "AutoCheck", "rubro": "Automotor", "ubicacion": "Córdoba", "estado": "Activa"},
        {"slug": "estetica-norte", "nombre": "Estética Norte", "rubro": "Belleza", "ubicacion": "Buenos Aires", "estado": "Activa"},
        {"slug": "centro-odonto", "nombre": "Centro Odonto", "rubro": "Salud", "ubicacion": "Rosario", "estado": "Activa"},
        {"slug": "vital-gym", "nombre": "Vital Gym", "rubro": "Fitness", "ubicacion": "Mendoza", "estado": "Activa"},
        {"slug": "taller-rivera", "nombre": "Taller Rivera", "rubro": "Automotor", "ubicacion": "San Juan", "estado": "Activa"},
    ]
    rubros = sorted({empresa["rubro"] for empresa in empresas})
    return render(
        request,
        "servicios.html",
        {
            "empresas": empresas,
            "rubros": rubros,
        },
    )


def solicitar_turno(request, slug):
    empresas = {
        "clinica-andina": {"nombre": "Clínica Andina", "rubro": "Salud"},
        "autocheck": {"nombre": "AutoCheck", "rubro": "Automotor"},
        "estetica-norte": {"nombre": "Estética Norte", "rubro": "Belleza"},
        "centro-odonto": {"nombre": "Centro Odonto", "rubro": "Salud"},
        "vital-gym": {"nombre": "Vital Gym", "rubro": "Fitness"},
        "taller-rivera": {"nombre": "Taller Rivera", "rubro": "Automotor"},
    }
    empresa = empresas.get(slug)
    if not empresa:
        return redirect("servicios_publicos")

    horarios = [
        {"fecha": "Lunes 25", "hora": "09:00"},
        {"fecha": "Lunes 25", "hora": "10:30"},
        {"fecha": "Martes 26", "hora": "11:00"},
        {"fecha": "Martes 26", "hora": "14:00"},
        {"fecha": "Miércoles 27", "hora": "16:30"},
        {"fecha": "Jueves 28", "hora": "09:30"},
    ]
    return render(
        request,
        "servicios_turno.html",
        {
            "empresa": empresa,
            "horarios": horarios,
        },
    )


class UsuarioLoginView(LoginView):
    template_name = 'login.html'
    
    def get_success_url(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return '/dashboard/admin/'
        return '/dashboard/'

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return response
        usuario_empresas = user.empresas.select_related('empresa').order_by('fecha_alta', 'id')
        has_enabled_company = any(
            ue.activo and ue.empresa.activo and empresa_habilitada_por_suscripcion(ue.empresa)
            for ue in usuario_empresas
        )
        if not has_enabled_company:
            logout(self.request)
            form.add_error(None, "Tu empresa esta inactiva. Contacta al administrador.")
            return self.form_invalid(form)
        return response


class UsuarioLogoutView(LogoutView):
    next_page = '/'


@login_required
def dashboard(request):
    user = request.user
    if user.is_staff or user.is_superuser:
        return redirect('dashboard_admin')

    nombre = f'{user.nombre} {user.apellido}'.strip()
    empresas = get_user_empresas(user)
    empresas_habilitadas = [ue for ue in empresas if ue.activo and ue.empresa.activo and empresa_habilitada_por_suscripcion(ue.empresa)]
    if not empresas_habilitadas:
        logout(request)
        return redirect("login")

    if empresas.count() > 1:
        empresas_cards = []
        for ue in empresas:
            enabled = ue.activo and ue.empresa.activo and empresa_habilitada_por_suscripcion(ue.empresa)
            sus = get_suscripcion_actual(ue.empresa)
            empresas_cards.append(
                {
                    "usuario_empresa": ue,
                    "enabled": enabled,
                    "vencimiento": sus.fecha_vencimiento if sus else None,
                }
            )
        return render(
            request,
            'dashboard/seleccionar_empresa.html',
            {
                'empresas_cards': empresas_cards,
                'welcome_name': nombre or user.email,
                'role_label': role_label_for(user),
            },
        )

    if empresas.count() == 1:
        request.session["empresa_activa_id"] = empresas.first().empresa_id

    empresa_activa = get_active_usuario_empresa(user, request)
    if not empresa_activa:
        logout(request)
        return redirect("login")

    selected_date_str = request.GET.get("fecha", "")
    selected_date = timezone.now().date()
    try:
        if selected_date_str:
            selected_date = date.fromisoformat(selected_date_str)
    except ValueError:
        selected_date = timezone.now().date()

    turnos_qs = Turno.objects.filter(empresa_id=empresa_activa.empresa_id).select_related(
        "cliente",
        "servicio_empresa",
    ).order_by("fecha", "hora_inicio")

    calendar_items = []
    for turno in turnos_qs:
        cliente_nombre = f"{turno.cliente.nombre} {turno.cliente.apellido}".strip() or turno.cliente.email
        label = f"{turno.hora_inicio.strftime('%H:%M')} - {turno.servicio_empresa.nombre} - {cliente_nombre}"
        calendar_items.append(
            {
                "id": turno.id,
                "date": turno.fecha.isoformat(),
                "label": label,
                "estado": turno.estado,
            }
        )

    return render(
        request,
        'dashboard/index.html',
        {
            'welcome_name': nombre or user.email,
            'role_label': role_label_for_usuario_empresa(empresa_activa),
            'company_name': empresa_activa.empresa.nombre,
            'selected_date': selected_date,
            'calendar_items': calendar_items,
        },
    )


@login_required
def dashboard_select_empresa(request, empresa_id):
    user = request.user
    if user.is_staff or user.is_superuser:
        return redirect('dashboard_admin')
    usuario_empresa = user.empresas.select_related('empresa').filter(empresa_id=empresa_id).first()
    if (
        not usuario_empresa
        or not usuario_empresa.activo
        or not usuario_empresa.empresa.activo
        or not empresa_habilitada_por_suscripcion(usuario_empresa.empresa)
    ):
        messages.error(request, "La empresa seleccionada esta inactiva.")
        return redirect('dashboard')
    request.session["empresa_activa_id"] = usuario_empresa.empresa_id
    return redirect('dashboard')


@login_required
def admin_dashboard(request):
    if not (request.user.is_staff or request.user.is_superuser):
        raise PermissionDenied
    return render(
        request,
        'dashboard/admin/index.html',
        admin_context(request.user),
    )


@login_required
def admin_empresas_nueva(request):
    if not (request.user.is_staff or request.user.is_superuser):
        raise PermissionDenied
    form = EmpresaCreateForm()
    if request.method == "POST":
        form = EmpresaCreateForm(request.POST)
        if form.is_valid():
            empresa = form.save(commit=False)
            empresa.save()
            Suscripcion.objects.create(
                empresa=empresa,
                plan=form.cleaned_data["plan"],
                periodicidad=form.cleaned_data["periodicidad"],
                activa=True,
                fecha_inicio=timezone.now().date(),
                fecha_vencimiento=None,
            )
            messages.success(request, "Empresa creada con suscripcion inicial.")
            return redirect("dashboard_admin_empresa")
    return render(
        request,
        "dashboard/admin/empresa_nueva.html",
        {
            "form": form,
            "paises": Pais.objects.order_by("nombre"),
            "provincias": Provincia.objects.select_related("pais").order_by("nombre"),
            "localidades": Localidad.objects.select_related("provincia").order_by("nombre"),
            **admin_context(request.user),
        },
    )


@login_required
def admin_usuarios_nuevo(request):
    if not (request.user.is_staff or request.user.is_superuser):
        raise PermissionDenied
    return render(request, 'dashboard/admin/usuario_nuevo.html', admin_context(request.user))


@login_required
def admin_complementos(request):
    if not (request.user.is_staff or request.user.is_superuser):
        raise PermissionDenied
    return render(request, 'dashboard/admin/complementos.html', admin_context(request.user))


@login_required
def admin_contabilidad(request):
    require_admin(request.user)
    today = timezone.now().date()
    start_month = today.replace(day=1)
    last_30 = today - timedelta(days=30)

    pagos = Pago.objects.select_related("suscripcion__empresa__rubro")
    rubro_id = request.GET.get("rubro") or ""
    year = request.GET.get("year") or ""
    month = request.GET.get("month") or ""

    if rubro_id.isdigit():
        pagos = pagos.filter(suscripcion__empresa__rubro_id=int(rubro_id))
    if year.isdigit():
        pagos = pagos.filter(fecha_pago__year=int(year))
    if month.isdigit():
        pagos = pagos.filter(fecha_pago__month=int(month))
    ingresos_total = pagos.aggregate(total=Sum("monto"))["total"] or 0
    ingresos_mes = pagos.filter(fecha_pago__gte=start_month, fecha_pago__lte=today).aggregate(total=Sum("monto"))["total"] or 0
    ingresos_30 = pagos.filter(fecha_pago__gte=last_30, fecha_pago__lte=today).aggregate(total=Sum("monto"))["total"] or 0
    pagos_count = pagos.count()
    ticket_promedio = pagos.aggregate(avg=Avg("monto"))["avg"] or 0

    empresas_qs = Empresa.objects.all()
    if rubro_id.isdigit():
        empresas_qs = empresas_qs.filter(rubro_id=int(rubro_id))
    empresas_total = empresas_qs.count()

    # Fecha de corte para estado financiero:
    # - sin filtros temporales: hoy
    # - con anio/mes: cierre del periodo filtrado
    corte = today
    if year.isdigit() and month.isdigit():
        corte = date(int(year), int(month), 1)
        corte = add_months(corte, 1) - timedelta(days=1)
    elif year.isdigit():
        corte = date(int(year), 12, 31)
    elif month.isdigit():
        corte = date(today.year, int(month), 1)
        corte = add_months(corte, 1) - timedelta(days=1)

    empresas_al_dia = 0
    empresas_vencidas = 0
    empresas_por_vencer = 0
    por_vencer_limite = corte + timedelta(days=7)

    for empresa in empresas_qs:
        suscripcion = Suscripcion.objects.filter(empresa=empresa).order_by("-fecha_inicio").first()
        if not suscripcion:
            continue
        if suscripcion.fecha_vencimiento is None:
            # Sin vencimiento explicitado, se considera al dia en el corte.
            empresas_al_dia += 1
            continue
        if suscripcion.fecha_vencimiento < corte:
            empresas_vencidas += 1
        elif suscripcion.fecha_vencimiento <= por_vencer_limite:
            empresas_por_vencer += 1
            empresas_al_dia += 1
        else:
            empresas_al_dia += 1

    # Ultimos 6 meses de ingresos
    monthly = []
    for i in range(5, -1, -1):
        month_start = add_months(start_month, -i).replace(day=1)
        month_end = (add_months(month_start, 1) - timedelta(days=1))
        total = pagos.filter(fecha_pago__gte=month_start, fecha_pago__lte=month_end).aggregate(total=Sum("monto"))["total"] or 0
        monthly.append({"label": month_start.strftime("%b %Y"), "total": total})

    rubros = Rubro.objects.order_by("nombre")
    years = Pago.objects.dates("fecha_pago", "year", order="DESC")

    return render(
        request,
        "dashboard/admin/contabilidad.html",
        {
            "ingresos_total": ingresos_total,
            "ingresos_mes": ingresos_mes,
            "ingresos_30": ingresos_30,
            "pagos_count": pagos_count,
            "ticket_promedio": ticket_promedio,
            "empresas_total": empresas_total,
            "empresas_al_dia": empresas_al_dia,
            "empresas_vencidas": empresas_vencidas,
            "empresas_por_vencer": empresas_por_vencer,
            "estado_corte": corte,
            "monthly": monthly,
            "rubros": rubros,
            "years": years,
            "filter_rubro": rubro_id,
            "filter_year": year,
            "filter_month": month,
            **admin_context(request.user),
        },
    )


@login_required
def admin_empresas_lista(request):
    if not (request.user.is_staff or request.user.is_superuser):
        raise PermissionDenied
    return redirect('dashboard_admin_empresa')


@login_required
def admin_empresa(request):
    require_admin(request.user)
    query = request.GET.get("q", "").strip()
    status = request.GET.get("estado", "").strip()
    empresas = Empresa.objects.order_by("nombre")
    if query:
        empresas = empresas.filter(nombre__icontains=query)
    if status == "activas":
        empresas = empresas.filter(activo=True)
    elif status == "inactivas":
        empresas = empresas.filter(activo=False)
    empresas_data = []
    for empresa in empresas:
        suscripcion = get_suscripcion_actual(empresa)
        empresas_data.append(
            {
                "empresa": empresa,
                "vencimiento": suscripcion.fecha_vencimiento if suscripcion else None,
            }
        )
    return render(
        request,
        "dashboard/admin/empresa.html",
        {
            "empresas_data": empresas_data,
            "query": query,
            "status": status,
            **admin_context(request.user),
        },
    )


@login_required
def admin_empresa_editar(request, empresa_id):
    require_admin(request.user)
    empresa = Empresa.objects.get(pk=empresa_id)
    empresa_form = EmpresaForm(instance=empresa)
    suscripcion_actual = get_suscripcion_actual(empresa)
    pagos = Pago.objects.filter(suscripcion__empresa=empresa).order_by("-fecha_pago")
    pago_form = PagoForm(suscripcion=suscripcion_actual)
    monto_a_cobrar = monto_por_suscripcion(suscripcion_actual)

    if request.method == "POST":
        form_type = request.POST.get("form_type")
        if form_type == "empresa":
            empresa_form = EmpresaForm(request.POST, instance=empresa)
            if empresa_form.is_valid():
                empresa_form.save()
                messages.success(request, "Empresa actualizada correctamente.")
                return redirect("dashboard_admin_empresa_editar", empresa_id=empresa.id)
        elif form_type == "pago":
            pago_form = PagoForm(request.POST, suscripcion=suscripcion_actual)
            if pago_form.is_valid():
                pago = Pago.objects.create(
                    suscripcion=suscripcion_actual,
                    fecha_pago=timezone.now().date(),
                    monto=monto_por_suscripcion(suscripcion_actual),
                    periodo=suscripcion_actual.periodicidad,
                )
                actualizar_vencimiento_por_pago(suscripcion_actual, pago)
                messages.success(request, "Pago registrado y suscripcion actualizada.")
                return redirect("dashboard_admin_empresa_editar", empresa_id=empresa.id)

    usuarios = UsuarioEmpresa.objects.filter(empresa=empresa).select_related("usuario").order_by("usuario__nombre")
    return render(
        request,
        "dashboard/admin/empresa_editar.html",
        {
            "empresa": empresa,
            "empresa_form": empresa_form,
            "suscripcion": suscripcion_actual,
            "pagos": pagos,
            "pago_form": pago_form,
            "monto_a_cobrar": monto_a_cobrar,
            "usuarios": usuarios,
            "paises": Pais.objects.order_by("nombre"),
            "provincias": Provincia.objects.select_related("pais").order_by("nombre"),
            "localidades": Localidad.objects.select_related("provincia").order_by("nombre"),
            **admin_context(request.user),
        },
    )


def add_months(base_date, months):
    year = base_date.year + (base_date.month - 1 + months) // 12
    month = (base_date.month - 1 + months) % 12 + 1
    day = base_date.day
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    last_day = (next_month - timedelta(days=1)).day
    if day > last_day:
        day = last_day
    return date(year, month, day)


def get_suscripcion_actual(empresa):
    suscripcion = Suscripcion.objects.filter(empresa=empresa).order_by("-fecha_inicio").first()
    if suscripcion:
        sync_estado_suscripcion(suscripcion)
    return suscripcion


def sync_estado_suscripcion(suscripcion, today=None):
    today = today or timezone.now().date()
    if suscripcion.fecha_vencimiento and suscripcion.fecha_vencimiento < today and suscripcion.activa:
        suscripcion.activa = False
        suscripcion.save(update_fields=["activa"])
    return suscripcion


def empresa_habilitada_por_suscripcion(empresa):
    suscripcion = get_suscripcion_actual(empresa)
    if not suscripcion:
        return False
    return suscripcion.activa


def actualizar_vencimiento_por_pago(suscripcion, pago):
    base = suscripcion.fecha_vencimiento or suscripcion.fecha_inicio
    if pago.periodo == Suscripcion.PERIODO_MENSUAL:
        nuevo = add_months(base, 1)
    else:
        nuevo = add_months(base, 12)
    suscripcion.fecha_vencimiento = nuevo
    suscripcion.activa = True
    suscripcion.save()


def monto_por_suscripcion(suscripcion):
    if not suscripcion:
        return 0
    if suscripcion.periodicidad == Suscripcion.PERIODO_ANUAL:
        return suscripcion.plan.precio_anual
    return suscripcion.plan.precio_mensual


def build_usuario_pdf(data):
    def sanitize(text):
        return "".join(ch if 32 <= ord(ch) <= 126 else " " for ch in text)

    def escape_pdf(text):
        return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    title = "Usuario creado - Gestion Turnos"
    body_lines = [
        f"Empresa: {data.get('empresa', '')}",
        f"Nombre: {data.get('nombre', '')}",
        f"Email: {data.get('email', '')}",
        f"DNI: {data.get('dni', '')}",
        f"Telefono: {data.get('telefono', '')}",
        f"Rol: {data.get('rol', '')}",
        f"Password: {data.get('password', '')}",
    ]
    note = "IMPORTANTE: Cambiar la contrasena al primer ingreso."

    title = escape_pdf(sanitize(title))
    body_lines = [escape_pdf(sanitize(line)) for line in body_lines]
    note = escape_pdf(sanitize(note))

    title_size = 16
    body_size = 13
    note_size = 13
    title_width = len(title) * 6
    title_x = max(50, int((612 - title_width) / 2))
    title_y = 760
    underline_y = title_y - 4

    content = (
        f"BT /F2 {title_size} Tf {title_x} {title_y} Td ({title}) Tj ET "
        f"{title_x} {underline_y} m {title_x + title_width} {underline_y} l S "
        f"BT /F1 {body_size} Tf 50 720 Td "
    )
    for line in body_lines:
        content += f"({line}) Tj 0 -20 Td "
    content += f"/F2 {note_size} Tf ({note}) Tj ET"

    content_bytes = content.encode("ascii", errors="ignore")
    xref = []
    pdf = b"%PDF-1.4\n"

    def add_object(obj):
        xref.append(len(pdf))
        return obj

    obj1 = add_object(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    obj2 = add_object(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
    obj3 = add_object(b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R /F2 6 0 R >> >> /Contents 5 0 R >>\nendobj\n")
    obj4 = add_object(b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")
    obj6 = add_object(b"6 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>\nendobj\n")
    obj5_stream = b"5 0 obj\n<< /Length " + str(len(content_bytes)).encode("ascii") + b" >>\nstream\n" + content_bytes + b"\nendstream\nendobj\n"
    obj5 = add_object(obj5_stream)

    pdf += obj1 + obj2 + obj3 + obj4 + obj5 + obj6
    xref_start = len(pdf)
    pdf += b"xref\n0 7\n0000000000 65535 f \n"
    for offset in xref:
        pdf += f"{offset:010d} 00000 n \n".encode("ascii")
    pdf += b"trailer\n<< /Size 7 /Root 1 0 R >>\nstartxref\n" + str(xref_start).encode("ascii") + b"\n%%EOF"
    return pdf


@login_required
def admin_empresa_suscripcion_editar(request, empresa_id):
    require_admin(request.user)
    empresa = Empresa.objects.get(pk=empresa_id)
    suscripcion = Suscripcion.objects.filter(empresa=empresa).order_by("-fecha_inicio").first()
    if not suscripcion:
        messages.error(request, "La empresa no tiene suscripcion para editar.")
        return redirect("dashboard_admin_empresa_editar", empresa_id=empresa.id)

    form = SuscripcionEditForm(instance=suscripcion)
    if request.method == "POST":
        form = SuscripcionEditForm(request.POST, instance=suscripcion)
        if form.is_valid():
            form.save()
            messages.success(request, "Suscripcion actualizada correctamente.")
            return redirect("dashboard_admin_empresa_editar", empresa_id=empresa.id)
    return render(
        request,
        "dashboard/admin/empresa_suscripcion_editar.html",
        {
            "empresa": empresa,
            "suscripcion": suscripcion,
            "form": form,
            **admin_context(request.user),
        },
    )


@login_required
def admin_empresa_usuario_nuevo(request, empresa_id):
    require_admin(request.user)
    empresa = Empresa.objects.get(pk=empresa_id)
    form = UsuarioEmpresaCreateForm()
    if request.method == "POST":
        form = UsuarioEmpresaCreateForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            with transaction.atomic():
                user_model = get_user_model()
                password = "gestorturnos2026"
                user = user_model.objects.create_user(
                    email=data["email"],
                    password=password,
                    nombre=data["nombre"],
                    apellido=data["apellido"],
                    dni=data["dni"],
                    telefono=data["telefono"],
                )
                UsuarioEmpresa.objects.create(
                    usuario=user,
                    empresa=empresa,
                    rol=data["rol"],
                    activo=True,
                )
            pdf_bytes = build_usuario_pdf(
                {
                    "empresa": empresa.nombre,
                    "nombre": f"{user.nombre} {user.apellido}",
                    "email": user.email,
                    "dni": user.dni,
                    "telefono": user.telefono,
                    "rol": data["rol"],
                    "password": password,
                }
            )
            pdf_base64 = base64.b64encode(pdf_bytes).decode("ascii")
            return render(
                request,
                "dashboard/admin/usuario_pdf_descarga.html",
                {
                    "pdf_base64": pdf_base64,
                    "filename": f"usuario_{user.id}.pdf",
                    "redirect_url": f"/dashboard/admin/empresa/{empresa.id}/",
                    **admin_context(request.user),
                },
            )
    return render(
        request,
        "dashboard/admin/empresa_usuario_nuevo.html",
        {
            "empresa": empresa,
            "form": form,
            **admin_context(request.user),
        },
    )


@login_required
def admin_empresa_usuario_editar(request, empresa_id, usuario_id):
    require_admin(request.user)
    empresa = Empresa.objects.get(pk=empresa_id)
    usuario_empresa = UsuarioEmpresa.objects.select_related("usuario").get(
        empresa=empresa,
        usuario_id=usuario_id,
    )
    user = usuario_empresa.usuario
    initial = {
        "rol": usuario_empresa.rol,
        "email": user.email,
        "nombre": user.nombre,
        "apellido": user.apellido,
        "dni": user.dni,
        "telefono": user.telefono,
    }
    form = UsuarioEmpresaEditForm(initial=initial, user_instance=user)
    if request.method == "POST":
        action = request.POST.get("action", "save")
        if action == "reset_password":
            password = "gestorturnos2026"
            user.set_password(password)
            user.save()
            pdf_bytes = build_usuario_pdf(
                {
                    "empresa": empresa.nombre,
                    "nombre": f"{user.nombre} {user.apellido}",
                    "email": user.email,
                    "dni": user.dni,
                    "telefono": user.telefono,
                    "rol": usuario_empresa.rol,
                    "password": password,
                }
            )
            pdf_base64 = base64.b64encode(pdf_bytes).decode("ascii")
            return render(
                request,
                "dashboard/admin/usuario_pdf_descarga.html",
                {
                    "pdf_base64": pdf_base64,
                    "filename": f"usuario_{user.id}.pdf",
                    "redirect_url": f"/dashboard/admin/empresa/{empresa.id}/",
                    **admin_context(request.user),
                },
            )
        form = UsuarioEmpresaEditForm(request.POST, user_instance=user)
        if form.is_valid():
            data = form.cleaned_data
            user.email = data["email"]
            user.username = data["email"]
            user.nombre = data["nombre"]
            user.apellido = data["apellido"]
            user.dni = data["dni"]
            user.telefono = data["telefono"]
            user.save()
            usuario_empresa.rol = data["rol"]
            usuario_empresa.save()
            messages.success(request, "Usuario actualizado correctamente.")
            return redirect("dashboard_admin_empresa_editar", empresa_id=empresa.id)
    return render(
        request,
        "dashboard/admin/empresa_usuario_editar.html",
        {
            "empresa": empresa,
            "usuario_empresa": usuario_empresa,
            "form": form,
            **admin_context(request.user),
        },
    )


@login_required
@require_POST
def admin_empresa_usuario_eliminar(request, empresa_id, usuario_id):
    require_admin(request.user)
    empresa = Empresa.objects.get(pk=empresa_id)
    usuario_empresa = UsuarioEmpresa.objects.select_related("usuario").get(
        empresa=empresa,
        usuario_id=usuario_id,
    )
    user = usuario_empresa.usuario

    relaciones = UsuarioEmpresa.objects.filter(usuario=user)
    if relaciones.count() > 1:
        usuario_empresa.delete()
        messages.success(request, "Usuario desvinculado de la empresa.")
    else:
        user.delete()
        messages.success(request, "Usuario eliminado correctamente.")

    return redirect("dashboard_admin_empresa_editar", empresa_id=empresa.id)


def require_admin(user):
    if not (user.is_staff or user.is_superuser):
        raise PermissionDenied


def role_label_for(user):
    if user.is_staff or user.is_superuser:
        return "Administrador del sistema"
    return "Usuario"


def role_label_for_usuario_empresa(usuario_empresa):
    if not usuario_empresa:
        return "Usuario"
    if usuario_empresa.rol == UsuarioEmpresa.ROL_DUENO:
        return "Propietario"
    return "Usuario"


def get_active_empresa_name(user, request=None):
    usuario_empresa = get_active_usuario_empresa(user, request)
    if not usuario_empresa:
        return None
    return usuario_empresa.empresa.nombre


def get_active_usuario_empresa(user, request=None):
    empresas = get_user_empresas(user)
    if not empresas:
        return None

    if request:
        empresa_id = request.session.get("empresa_activa_id")
        if empresa_id:
            selected = empresas.filter(empresa_id=empresa_id).first()
            if selected and selected.activo and selected.empresa.activo and empresa_habilitada_por_suscripcion(selected.empresa):
                return selected

    for usuario_empresa in empresas:
        if usuario_empresa.activo and usuario_empresa.empresa.activo and empresa_habilitada_por_suscripcion(usuario_empresa.empresa):
            return usuario_empresa

    return None


def get_user_empresas(user):
    return user.empresas.select_related('empresa').order_by('fecha_alta', 'id')


def admin_context(user):
    nombre = f'{user.nombre} {user.apellido}'.strip()
    return {
        "welcome_name": nombre or user.email,
        "role_label": role_label_for(user),
        "company_name": get_active_empresa_name(user),
    }


@login_required
def admin_complemento_rubros(request):
    require_admin(request.user)
    if request.method == "POST":
        form = RubroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Rubro creado correctamente.")
            return redirect("dashboard_admin_complemento_rubros")
    else:
        form = RubroForm()
    items = Rubro.objects.order_by("nombre")
    return render(
        request,
        "dashboard/admin/complemento_form.html",
        {
            "title": "Rubros",
            "description": "Carga rubros base para clasificar empresas y servicios.",
            "form": form,
            "items_title": "Rubros cargados",
            "items": items,
            **admin_context(request.user),
        },
    )


@login_required
def admin_complemento_paises(request):
    require_admin(request.user)
    if request.method == "POST":
        form = PaisForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Pais creado correctamente.")
            return redirect("dashboard_admin_complemento_paises")
    else:
        form = PaisForm()
    items = Pais.objects.order_by("nombre")
    return render(
        request,
        "dashboard/admin/complemento_form.html",
        {
            "title": "Paises",
            "description": "Carga paises base para la configuracion geografica.",
            "form": form,
            "items_title": "Paises cargados",
            "items": items,
            **admin_context(request.user),
        },
    )


@login_required
def admin_complemento_provincias(request):
    require_admin(request.user)
    if request.method == "POST":
        form = ProvinciaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Provincia creada correctamente.")
            return redirect("dashboard_admin_complemento_provincias")
    else:
        form = ProvinciaForm()
    ordered_fields = [form[name] for name in ["pais", "nombre"] if name in form.fields]
    items = Provincia.objects.select_related("pais").order_by("nombre")
    items_payload = [
        {"label": str(item), "parent_id": item.pais_id}
        for item in items
    ]
    return render(
        request,
        "dashboard/admin/complemento_form.html",
        {
            "title": "Provincias",
            "description": "Carga provincias asociadas a cada pais.",
            "form": form,
            "field_ordered": ordered_fields,
            "items_title": "Provincias cargadas",
            "items_payload": items_payload,
            "filter_select_id": form["pais"].id_for_label,
            "filter_empty_text": "Selecciona un pais para ver provincias cargadas.",
            **admin_context(request.user),
        },
    )


@login_required
def admin_complemento_localidades(request):
    require_admin(request.user)
    if request.method == "POST":
        form = LocalidadForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Localidad creada correctamente.")
            return redirect("dashboard_admin_complemento_localidades")
    else:
        form = LocalidadForm()
    ordered_fields = [form[name] for name in ["provincia", "nombre"] if name in form.fields]
    items = Localidad.objects.select_related("provincia").order_by("nombre")
    items_payload = [
        {"label": str(item), "parent_id": item.provincia_id}
        for item in items
    ]
    return render(
        request,
        "dashboard/admin/complemento_form.html",
        {
            "title": "Localidades",
            "description": "Carga localidades asociadas a cada provincia.",
            "form": form,
            "field_ordered": ordered_fields,
            "items_title": "Localidades cargadas",
            "items_payload": items_payload,
            "filter_select_id": form["provincia"].id_for_label,
            "filter_empty_text": "Selecciona una provincia para ver localidades cargadas.",
            **admin_context(request.user),
        },
    )


@login_required
def admin_complemento_planes(request):
    require_admin(request.user)
    if request.method == "POST":
        form = PlanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Plan creado correctamente.")
            return redirect("dashboard_admin_complemento_planes")
    else:
        form = PlanForm()
    items = Plan.objects.order_by("nombre")
    return render(
        request,
        "dashboard/admin/complemento_form.html",
        {
            "title": "Planes",
            "description": "Carga planes base para suscripciones.",
            "form": form,
            "items_title": "Planes cargados",
            "items": items,
            **admin_context(request.user),
        },
    )


@login_required
def admin_complemento_servicios_base(request):
    require_admin(request.user)
    if request.method == "POST":
        form = ServicioBaseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Servicio base creado correctamente.")
            return redirect("dashboard_admin_complemento_servicios_base")
    else:
        form = ServicioBaseForm()
    ordered_fields = [form[name] for name in ["rubro", "nombre"] if name in form.fields]
    items = ServicioBase.objects.select_related("rubro").order_by("nombre")
    items_payload = [
        {"label": str(item), "parent_id": item.rubro_id}
        for item in items
    ]
    return render(
        request,
        "dashboard/admin/complemento_form.html",
        {
            "title": "Servicios base",
            "description": "Carga servicios base por rubro.",
            "form": form,
            "field_ordered": ordered_fields,
            "items_title": "Servicios base cargados",
            "items_payload": items_payload,
            "filter_select_id": form["rubro"].id_for_label,
            "filter_empty_text": "Selecciona un rubro para ver servicios cargados.",
            **admin_context(request.user),
        },
    )


@login_required
def admin_complemento_suscripciones(request):
    require_admin(request.user)
    if request.method == "POST":
        form = SuscripcionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Suscripcion creada correctamente.")
            return redirect("dashboard_admin_complemento_suscripciones")
    else:
        form = SuscripcionForm()
    items = Suscripcion.objects.select_related("empresa", "plan").order_by("-fecha_inicio")
    return render(
        request,
        "dashboard/admin/complemento_form.html",
        {
            "title": "Suscripciones",
            "description": "Carga suscripciones asociadas a empresas.",
            "form": form,
            "items_title": "Suscripciones cargadas",
            "items": items,
            **admin_context(request.user),
        },
    )
