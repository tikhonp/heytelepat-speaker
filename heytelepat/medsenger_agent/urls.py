from django.urls import path
from medsenger_agent import views

urlpatterns = [
    path('init', views.InitApiView.as_view()),
    path('remove', views.RemoveApiView.as_view()),
    path('status', views.StatusApiView.as_view()),
    path('settings', views.settingsAPI),
    path('message', views.MessageApiView.as_view()),
    path('newdevice', views.newdevice),
    path('order', views.order),
]
