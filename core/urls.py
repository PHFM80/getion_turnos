from django.urls import path

from core import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.UsuarioLoginView.as_view(), name='login'),
    path('logout/', views.UsuarioLogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='dashboard_admin'),
    path('dashboard/admin/empresas/nueva/', views.admin_empresas_nueva, name='dashboard_admin_empresa_nueva'),
    path('dashboard/admin/usuarios/nuevo/', views.admin_usuarios_nuevo, name='dashboard_admin_usuario_nuevo'),
    path('dashboard/admin/complementos/', views.admin_complementos, name='dashboard_admin_complementos'),
    path('dashboard/admin/complementos/rubros/', views.admin_complemento_rubros, name='dashboard_admin_complemento_rubros'),
    path('dashboard/admin/complementos/paises/', views.admin_complemento_paises, name='dashboard_admin_complemento_paises'),
    path('dashboard/admin/complementos/provincias/', views.admin_complemento_provincias, name='dashboard_admin_complemento_provincias'),
    path('dashboard/admin/complementos/localidades/', views.admin_complemento_localidades, name='dashboard_admin_complemento_localidades'),
    path('dashboard/admin/complementos/planes/', views.admin_complemento_planes, name='dashboard_admin_complemento_planes'),
    path('dashboard/admin/complementos/servicios-base/', views.admin_complemento_servicios_base, name='dashboard_admin_complemento_servicios_base'),
    path('dashboard/admin/complementos/suscripciones/', views.admin_complemento_suscripciones, name='dashboard_admin_complemento_suscripciones'),
    path('dashboard/admin/empresas/', views.admin_empresas_lista, name='dashboard_admin_empresas'),
]
