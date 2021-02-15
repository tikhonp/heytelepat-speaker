from rest_framework import serializers
from medsenger_agent.models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class CommentSerializer(serializers.Serializer):
    message = serializers.CharField()
    token = serializers.CharField()
