from django.urls import path

from core import views

urlpatterns = [
    path('', views.index, name='index'),
    path('servicios/', views.servicios_publicos, name='servicios_publicos'),
    path('servicios/turno/<slug:slug>/', views.solicitar_turno, name='servicios_turno'),
    path('login/', views.UsuarioLoginView.as_view(), name='login'),
    path('logout/', views.UsuarioLogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/empresa/<int:empresa_id>/', views.dashboard_select_empresa, name='dashboard_select_empresa'),
    path('dashboard/admin/', views.admin_dashboard, name='dashboard_admin'),
    path('dashboard/admin/empresa/', views.admin_empresa, name='dashboard_admin_empresa'),
    path('dashboard/admin/empresa/<int:empresa_id>/', views.admin_empresa_editar, name='dashboard_admin_empresa_editar'),
    path('dashboard/admin/empresa/<int:empresa_id>/suscripcion/', views.admin_empresa_suscripcion_editar, name='dashboard_admin_empresa_suscripcion_editar'),
    path('dashboard/admin/empresa/<int:empresa_id>/usuarios/nuevo/', views.admin_empresa_usuario_nuevo, name='dashboard_admin_empresa_usuario_nuevo'),
    path('dashboard/admin/empresa/<int:empresa_id>/usuarios/<int:usuario_id>/editar/', views.admin_empresa_usuario_editar, name='dashboard_admin_empresa_usuario_editar'),
    path('dashboard/admin/empresa/<int:empresa_id>/usuarios/<int:usuario_id>/eliminar/', views.admin_empresa_usuario_eliminar, name='dashboard_admin_empresa_usuario_eliminar'),
    path('dashboard/admin/empresas/nueva/', views.admin_empresas_nueva, name='dashboard_admin_empresa_nueva'),
    path('dashboard/admin/usuarios/', views.admin_usuarios_nuevo, name='dashboard_admin_usuarios'),
    path('dashboard/admin/usuarios/nuevo/', views.admin_usuarios_nuevo, name='dashboard_admin_usuario_nuevo'),
    path('dashboard/admin/complementos/', views.admin_complementos, name='dashboard_admin_complementos'),
    path('dashboard/admin/contabilidad/', views.admin_contabilidad, name='dashboard_admin_contabilidad'),
    path('dashboard/admin/complementos/rubros/', views.admin_complemento_rubros, name='dashboard_admin_complemento_rubros'),
    path('dashboard/admin/complementos/paises/', views.admin_complemento_paises, name='dashboard_admin_complemento_paises'),
    path('dashboard/admin/complementos/provincias/', views.admin_complemento_provincias, name='dashboard_admin_complemento_provincias'),
    path('dashboard/admin/complementos/localidades/', views.admin_complemento_localidades, name='dashboard_admin_complemento_localidades'),
    path('dashboard/admin/complementos/planes/', views.admin_complemento_planes, name='dashboard_admin_complemento_planes'),
    path('dashboard/admin/complementos/servicios-base/', views.admin_complemento_servicios_base, name='dashboard_admin_complemento_servicios_base'),
    path('dashboard/admin/complementos/suscripciones/', views.admin_complemento_suscripciones, name='dashboard_admin_complemento_suscripciones'),
    path('dashboard/admin/empresas/', views.admin_empresas_lista, name='dashboard_admin_empresas'),
]
