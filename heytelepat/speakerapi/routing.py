from django.urls import path

from speakerapi.consumers import WSTest


ws_urlpatterns = [
    path('speakerapi/test/', WSTest.as_asgi())
]
