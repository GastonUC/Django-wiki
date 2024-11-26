from django.urls import path

from . import views

app_name = "wiki"
urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.entry, name="title"),
    path("new", views.new, name="new"),
    path("search", views.search, name="search"),
    path("wiki/<str:title>", views.random, name="random"),
    path("edit/<str:name>", views.edit, name="edit")
]
