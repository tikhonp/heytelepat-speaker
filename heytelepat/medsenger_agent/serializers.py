from rest_framework import serializers


class MessageDataSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    text = serializers.CharField()
    date = serializers.DateTimeField(format="%Y-%m-%d %H:%i:%s")


class MessageSerializer(serializers.Serializer):
    api_key = serializers.CharField()
    contract_id = serializers.IntegerField()
    message = MessageDataSerializer()
