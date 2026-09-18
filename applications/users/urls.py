from django.urls import path
from . import views

app_name = 'app_users'

urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('login/', views.LoginUser.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('update/', views.UpdatePasswordView.as_view(), name='user-update'),
    path('perfil/', views.MiPerfilView.as_view(), name='mi_perfil'),
    path('gestion/', views.UsuarioListView.as_view(), name='usuario_lista'),
    path('gestion/crear/', views.UsuarioCreateView.as_view(), name='usuario_crear'),
    path('gestion/<int:pk>/', views.UsuarioDetailView.as_view(), name='usuario_detalle'),
    path('gestion/<int:pk>/editar/', views.UsuarioUpdateView.as_view(), name='usuario_editar'),
    path('gestion/<int:pk>/password/', views.UsuarioPasswordResetView.as_view(), name='usuario_password'),
    path('gestion/<int:pk>/toggle/', views.UsuarioToggleView.as_view(), name='usuario_toggle'),
    path('gestion/<int:pk>/eliminar/', views.UsuarioDeleteView.as_view(), name='usuario_eliminar'),
    path('', views.DashboardView.as_view(), name='dashboard'),
]