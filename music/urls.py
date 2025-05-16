from django.urls import path
from . import views
from .views import audio_detail

urlpatterns = [
    path('', views.audio_list, name='audio_list'),
    path('audio/<slug:slug>/', audio_detail, name='audio_detail'),
    path('download/<slug:slug>/', views.download_audio, name='download_audio'),
    path('like/<int:audio_id>/', views.like_audio, name='like_audio'),
]
