from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('essay/', views.essay, name='essay'),
    path('essay/<int:pk>/', views.essay_detail, name='essay_detail'),
]
