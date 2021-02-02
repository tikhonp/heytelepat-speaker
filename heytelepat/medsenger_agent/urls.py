from django.urls import path
from medsenger_agent import views

urlpatterns = [
    path('init', views.init),
    path('remove', views.remove),
    path('status', views.status),
    path('settings', views.settings),
    path('message', views.message),
    path('action', views.action),
    path('newdevice/', views.newdevice),
]
