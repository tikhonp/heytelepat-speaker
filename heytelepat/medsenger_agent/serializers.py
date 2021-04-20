from rest_framework import serializers
from django.utils import timezone


class MessageDataSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    text = serializers.CharField()
    date = serializers.DateTimeField(
        format="%Y-%m-%d %H:%i:%s",
        default_timezone=timezone.utc,
    )


class MessageSerializer(serializers.Serializer):
    api_key = serializers.CharField()
    contract_id = serializers.IntegerField()
    message = MessageDataSerializer()
