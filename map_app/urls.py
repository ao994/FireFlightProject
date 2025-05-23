# imports
from django.urls import path

from . import views

# place all accessible URLs and their corresponding views here
urlpatterns = [
    path("", views.index, name="index"),
    path("map/", views.map, name="Map"),
    path('enchanted-circle-map/', views.enchanted_circle_map, name='enchanted_circle_map'),
    path("instructions/", views.instructions, name="instructions"),
    path("download/", views.download, name="download"),
]