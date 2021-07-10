from channels.generic.websocket import WebsocketConsumer
from speakerapi import serializers
import time
from channels.generic.websocket import AsyncJsonWebsocketConsumer
import asyncio
from django.core import exceptions
from medsenger_agent.models import Speaker
from channels.db import database_sync_to_async


class WSTest(WebsocketConsumer):
    def connect(self):
        self.accept()

        for i in range(10):
            self.send("something {}".format(i))
            time.sleep(5)


class WaitForConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def receive_json(self, content, **kwargs):
        serializer = self.get_serializer(data=content)
        if serializer.is_valid():
            token = serializer.data['token']

            try:
                await database_sync_to_async(Speaker.objects.get)(
                    token=token)
            except Speaker.DoesNotExist:
                await self.send("Invalid token")
                await self.close()
                return

            while True:
                s = await database_sync_to_async(
                    Speaker.objects.select_related('contract').get)(
                        token=token)

                if s.contract is not None:
                    break
                await asyncio.sleep(1)

            await self.send('OK')
            await self.close()
            return

        await self.send_json(serializer.errors)
        await self.close()

    def get_serializer(self, *, data):
        return serializers.CheckAuthSerializer(data=data)
