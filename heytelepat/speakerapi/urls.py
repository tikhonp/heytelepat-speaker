from django.urls import path
from speakerapi import views

urlpatterns = [
    path('init/', views.init),
    path('remove/', views.remove),
    path('tasks/', views.TaskApiView.as_view()),
    path('sendmessage/', views.send_message),
]
