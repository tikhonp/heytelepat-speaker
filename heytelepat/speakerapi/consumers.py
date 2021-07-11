from speakerapi import serializers
from django.core import serializers as dj_serializers
from channels.generic.websocket import AsyncJsonWebsocketConsumer
import asyncio
from medsenger_agent.models import Speaker, Message
from channels.db import database_sync_to_async


class WaitForAuthConsumer(AsyncJsonWebsocketConsumer):
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


class IncomingMessageNotifyConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def receive_json(self, content, **kwargs):
        serializer = serializers.IncomingMessageNotify(data=content)
        if serializer.is_valid():
            token = serializer.data['token']

            try:
                s = await database_sync_to_async(
                    Speaker.objects.select_related('contract').get)(
                        token=token)
            except Speaker.DoesNotExist:
                await self.send("Invalid token")
                await self.close()
                return

            if serializer.data['last_messages']:
                messages = None
                while messages is None or \
                        not await database_sync_to_async(messages.exists)():
                    messages = await database_sync_to_async(
                        Message.objects.filter)(
                            contract=s.contract, is_red=False)
                    await asyncio.sleep(5)

                text = dj_serializers.serialize(
                    'json', await database_sync_to_async(list)(messages),
                    fields=('text', 'date'))

                for message in messages:
                    message.is_red = True
                    message.is_notified = True
                    await database_sync_to_async(message.save)()

                print("here")
                await self.send(text)
                await self.close()
                return
            else:
                message = None
                while message is None:
                    try:
                        m = await database_sync_to_async(
                            Message.objects.filter)(
                                contract=s.contract, is_notified=False)
                        message = await database_sync_to_async(
                            m.earliest)('date')
                    except Message.DoesNotExist:
                        pass
                    await asyncio.sleep(5)
                text = dj_serializers.serialize(
                    'json', [message, ], fields=('text'))
                message.is_notified = True

                await database_sync_to_async(message.save)()

                await self.send(text)
                await self.close()
                return

        await self.send_json(serializer.errors)
        await self.close()
