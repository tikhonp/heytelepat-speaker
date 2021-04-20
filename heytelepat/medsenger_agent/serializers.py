from rest_framework import serializers


class MessageDataSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    text = serializers.CharField()
    date = serializers.CharField()
    sender = serializers.CharField()


class MessageSerializer(serializers.Serializer):
    api_key = serializers.CharField()
    contract_id = serializers.IntegerField()
    message = MessageDataSerializer()
