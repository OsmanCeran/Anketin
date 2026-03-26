from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "anketin"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("anketler/", views.AnketlerView.as_view(), name="anketler"),
    path("grafikler/", views.GrafiklerView.as_view(), name="grafikler"),
    path("<int:pk>/grafik/", views.GrafikDetayView.as_view(), name="grafik_detay"),
    path("anket-ekle/", views.anket_ekle, name="anket_ekle"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    path("<int:soru_id>/vote/", views.vote, name="vote"),
    path("<int:soru_id>/favori/", views.toggle_favori, name="toggle_favori"),
    
    # Auth ve Dashboard yönlendirmeleri
    path("profil/", views.dashboard, name="dashboard"),
    path("kayit/", views.kayit_ol, name="kayit"),
    path("login/", auth_views.LoginView.as_view(template_name='anketin/auth/login.html'), name="login"),
    path("logout/", views.custom_logout, name="logout"),
    
    # Yeni Anket Yönetimi Ekranları
    path("yonetim/", views.admin_dashboard, name="admin_dashboard"),
]
