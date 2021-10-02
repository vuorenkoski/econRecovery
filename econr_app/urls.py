from django.urls import path

from . import views

urlpatterns = [
    path('', views.index_view, name='index_view'),
    path('countries', views.countries_view, name='countries_view'),
    path('average', views.average_view, name='average_view'),
    path('world', views.world_view, name='world_view'),
    path('predictions', views.predictions_view, name='predictions_view'),
    path('about', views.about_view, name='about_view'),
]