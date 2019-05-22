from django.urls import path, include
from . import views

urlpatterns = [
    path('personalinfo/<int:pk>',
         views.RetrivePersonalInfo.as_view(),
         name='personalinfo'),
    path('skills/',
         views.ListSkills.as_view(),
         name='skills'),
    path('projects/',
         views.ListProjects.as_view(),
         name='projects'),
    path('create/',
         views.CreateMessage.as_view(),
         name='projects'),
    path('partners/',
         views.ListPartners.as_view(),
         name='partners'),
]
