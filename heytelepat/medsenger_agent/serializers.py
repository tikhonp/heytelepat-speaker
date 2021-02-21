from rest_framework import serializers
from django.conf import settings
from medsenger_agent.models import Message


def api_key_validator(value):
    if value != settings.APP_KEY:
        raise serializers.ValidationError("Invalid api key")


class MedsengerGenericSerializer(serializers.Serializer):
    api_key = serializers.CharField(
        max_length=255, validators=[api_key_validator])
    contract_id = serializers.IntegerField()


class InitSerializer(MedsengerGenericSerializer):
    preset = serializers.CharField(
        required=False, allow_null=True)
    params = serializers.CharField(
        required=False, allow_null=True)


class StatusSerializer(serializers.Serializer):
    api_key = serializers.CharField(
        max_length=255, validators=[api_key_validator])


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('message_id', 'text', 'date',)

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = User.objects.create(**validated_data)
        Profile.objects.create(user=user, **profile_data)
        return user

class MessageApiSerializer(MedsengerGenericSerializer):
    message = MessageSerializer()
