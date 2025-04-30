from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("map/", views.map, name="Map"),
    path('enchanted-circle-map/', views.enchanted_circle_map, name='enchanted_circle_map'),
    path("<str:modelName>/query/", views.query, name="query"),
    path("instructions/", views.instructions, name="instructions"),
    path("download/", views.download, name="download"),
]