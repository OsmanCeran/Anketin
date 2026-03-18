from django.urls import path
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
]
