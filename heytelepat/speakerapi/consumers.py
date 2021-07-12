from speakerapi import serializers
from django.core import serializers as dj_serializers
from channels.generic.websocket import AsyncJsonWebsocketConsumer
import asyncio
from medsenger_agent.models import Speaker, Message
from channels.db import database_sync_to_async


class WaitForAuthConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_group_name = None
        await self.accept()

    async def disconnect(self, close_code):
        if self.room_group_name is not None:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

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

            s = await database_sync_to_async(
                Speaker.objects.select_related('contract').get)(
                    token=token)

            if s.contract is not None:
                await self.send('OK')
                await self.close()
            else:
                self.room_group_name = 'auth_%s' % s.id
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
            return

        await self.send_json(serializer.errors)
        await self.close()

    async def receive_authed(self, event):
        await self.send('OK')
        await self.close()

    def get_serializer(self, *, data):
        return serializers.CheckAuthSerializer(data=data)


class IncomingMessageNotifyConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_group_name = None
        await self.accept()

    async def disconnect(self, close_code):
        if self.room_group_name is not None:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

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
                messages = await database_sync_to_async(
                    Message.objects.filter)(
                        contract=s.contract, is_red=False)

                if await database_sync_to_async(messages.exists)():
                    text = dj_serializers.serialize(
                        'json', await database_sync_to_async(list)(messages),
                        fields=('text', 'date'))

                    for message in messages:
                        message.is_red = True
                        message.is_notified = True
                        await database_sync_to_async(message.save)()

                    await self.send(text)
                    await self.close()
                    return
            else:
                message = None
                try:
                    m = await database_sync_to_async(
                        Message.objects.filter)(
                            contract=s.contract, is_notified=False)
                    message = await database_sync_to_async(
                        m.earliest)('date')
                except Message.DoesNotExist:
                    pass

                if message is not None:
                    text = dj_serializers.serialize(
                        'json', [message, ], fields=('text'))
                    message.is_notified = True

                    await database_sync_to_async(message.save)()

                    await self.send(text)
                    await self.close()
                    return

            self.room_group_name = 'message_%s' % s.contract.contract_id
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            return

        await self.send_json(serializer.errors)
        await self.close()

    async def receive_message(self, event):
        message = event['message']

        m = await database_sync_to_async(
            Message.objects.get)(id=event['message_id'])
        m.is_notified = True
        await database_sync_to_async(m.save)()

        await self.send_json([
            {
                "fields": {
                    "text": message
                }
            }
        ])
        await self.close()
