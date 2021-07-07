from rest_framework import serializers
from medsenger_agent.models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class CommentSerializer(serializers.Serializer):
    message = serializers.CharField()
    token = serializers.CharField()


class DataSendValuesSerializer(serializers.Serializer):
    category_name = serializers.CharField(),
    value = serializers.CharField(),


class SendValueSerializer(serializers.Serializer):
    token = serializers.CharField()
    values = serializers.ListField(child=DataSendValuesSerializer())


class CheckAuthSerializer(serializers.Serializer):
    token = serializers.CharField()


class IncomingMessageNotify(serializers.Serializer):
    token = serializers.CharField()
    last_messages = serializers.BooleanField()


class GetListOfAllCategories(serializers.Serializer):
    token = serializers.CharField()
    names_only = serializers.BooleanField()
