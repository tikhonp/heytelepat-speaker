from django.urls import path

from speakerapi import consumers


ws_urlpatterns = [
    path('ws/speakerapi/init/checkauth/',
         consumers.WaitForAuthConsumer.as_asgi()),
    path('ws/speakerapi/incomingmessage/',
         consumers.IncomingMessageNotifyConsumer.as_asgi()),
]
