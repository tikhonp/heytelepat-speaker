from django.urls import path

from speakerapi.consumers import WSTest, WaitForConsumer


ws_urlpatterns = [
    path('ws/speakerapi/test/', WSTest.as_asgi()),
    path('ws/speakerapi/init/checkauth/', WaitForConsumer.as_asgi()),
]
