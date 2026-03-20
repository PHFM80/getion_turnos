from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.shortcuts import render

from core.forms import (
    LocalidadForm,
    PaisForm,
    PlanForm,
    ProvinciaForm,
    RubroForm,
    ServicioBaseForm,
    SuscripcionForm,
)
from empresas.models import Rubro
from geo.models import Localidad, Pais, Provincia
from servicios.models import ServicioBase
from suscripciones.models import Plan, Suscripcion


def index(request):
    return render(request, 'index.html')


class UsuarioLoginView(LoginView):
    template_name = 'login.html'
    
    def get_success_url(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return '/dashboard/admin/'
        return '/dashboard/'


class UsuarioLogoutView(LogoutView):
    next_page = '/'


@login_required
def dashboard(request):
    user = request.user
    if user.is_staff or user.is_superuser:
        return redirect('dashboard_admin')

    nombre = f'{user.nombre} {user.apellido}'.strip()
    empresa_nombre = get_active_empresa_name(user)

    return render(
        request,
        'dashboard/index.html',
        {
            'welcome_name': nombre or user.email,
            'role_label': role_label_for(user),
            'company_name': empresa_nombre,
        },
    )


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
    return render(request, 'dashboard/admin/empresa_nueva.html', admin_context(request.user))


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
def admin_empresas_lista(request):
    if not (request.user.is_staff or request.user.is_superuser):
        raise PermissionDenied
    return render(request, 'dashboard/admin/empresas_lista.html', admin_context(request.user))


def require_admin(user):
    if not (user.is_staff or user.is_superuser):
        raise PermissionDenied


def role_label_for(user):
    if user.is_staff or user.is_superuser:
        return "Administrador del sistema"
    return "Usuario"


def get_active_empresa_name(user):
    usuario_empresa = user.empresas.filter(activo=True).select_related('empresa').first()
    if usuario_empresa:
        return usuario_empresa.empresa.nombre
    return None


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
