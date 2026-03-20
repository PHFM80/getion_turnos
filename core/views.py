from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.shortcuts import render


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
    empresa_nombre = None
    usuario_empresa = user.empresas.filter(activo=True).select_related('empresa').first()
    if usuario_empresa:
        empresa_nombre = usuario_empresa.empresa.nombre

    if empresa_nombre:
        role_label = f'Administrador de la empresa {empresa_nombre}'
    else:
        role_label = 'Administrador de la empresa'

    return render(
        request,
        'dashboard/index.html',
        {
            'welcome_name': nombre or user.email,
            'role_label': role_label,
        },
    )


@login_required
def admin_dashboard(request):
    if not (request.user.is_staff or request.user.is_superuser):
        raise PermissionDenied
    user = request.user
    nombre = f'{user.nombre} {user.apellido}'.strip()
    return render(
        request,
        'dashboard/admin/index.html',
        {
            'welcome_name': nombre or user.email,
            'role_label': 'Administrador del sistema',
        },
    )


@login_required
def admin_empresas_nueva(request):
    if not (request.user.is_staff or request.user.is_superuser):
        raise PermissionDenied
    return render(request, 'dashboard/admin/empresa_nueva.html')


@login_required
def admin_usuarios_nuevo(request):
    if not (request.user.is_staff or request.user.is_superuser):
        raise PermissionDenied
    return render(request, 'dashboard/admin/usuario_nuevo.html')


@login_required
def admin_complementos(request):
    if not (request.user.is_staff or request.user.is_superuser):
        raise PermissionDenied
    return render(request, 'dashboard/admin/complementos.html')


@login_required
def admin_empresas_lista(request):
    if not (request.user.is_staff or request.user.is_superuser):
        raise PermissionDenied
    return render(request, 'dashboard/admin/empresas_lista.html')
