from rest_framework import serializers
from medsenger_agent.models import Contract, Speaker, Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'task_type', 'datetime', 'is_done', )
