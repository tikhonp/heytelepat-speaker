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
    category_name = serializers.CharField(read_only=True),
    value = serializers.CharField(read_only=True),


class SendValueSerializer(serializers.Serializer):
    token = serializers.CharField()
    data = DataSendValuesSerializer(many=True)


class CheckAuthSerializer(serializers.Serializer):
    token = serializers.CharField()
