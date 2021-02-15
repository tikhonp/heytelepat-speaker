from django.urls import path
from speakerapi import views

urlpatterns = [
    path('init/', views.SpeakerInitApiView.as_view()),
    path('remove/', views.SpeakerDeleteApiView.as_view()),
    path('tasks/', views.TaskApiView.as_view()),
    path('sendmessage/', views.SendMessageApiView.as_view()),
]
