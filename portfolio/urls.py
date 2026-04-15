from django.urls import path
from portfolio import views

urlpatterns = [
    path('', views.home, name='index'),
    path('about/', views.about, name='about'),
    path('projects/', views.projects_view, name='projects'),
    path('skills/', views.skills_view, name='skills'),
    path('contact/', views.contact, name='contact'),
]
