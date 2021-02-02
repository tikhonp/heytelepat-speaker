from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from medsenger_agent.models import Speaker, Task
import json
from rest_framework import generics
from speakerapi import serializers
from django.core import exceptions
from rest_framework.exceptions import ValidationError
from medsenger_agent import agent_api

@csrf_exempt
@require_http_methods(["POST"])
def init(request):
    speaker = Speaker.objects.create()
    speaker.save()
    context = {
        'code': speaker.code,
        'token': speaker.token
    }
    response = HttpResponse(
        json.dumps(context), content_type='application/json')

    return response


@csrf_exempt
@require_http_methods(["POST"])
def remove(request):
    speaker = Speaker.objects.get(id=request.POST.get('id', ''))
    speaker.delete()
    return HttpResponse('ok')


class TaskApiView(generics.ListAPIView):
    serializer_class = serializers.TaskSerializer

    def get_queryset(self):
        token = self.request.data.get('token', '')
        try:
            queryset = Task.objects.filter(
                speaker=Speaker.objects.get(token=token),
                is_done=False
            )
            return queryset
        except exceptions.ObjectDoesNotExist:
            raise ValidationError(detail='Invalid Params')

    def patch(self, request):
        task_id = self.request.data.get('task_id', '')
        try:
            task = Task.objects.get(pk=int(task_id))
            task.is_done = True
            task.save()
            return HttpResponse("ok")
        except:
            raise ValidationError(detail='Invalid ID')


@csrf_exempt
@require_http_methods(["POST"])
def send_message(request):
    token = request.POST.get('token', '')
    try:
        speaker = Speaker.objects.get(token=token)
    except exceptions.ObjectDoesNotExist:
        response = HttpResponse("INVALID TOKEN")
        response.status_code = 400
        return response

    message = request.POST.get('message', '')
    agent_api.send_message(speaker.contract.contract_id, message)
    return HttpResponse("ok")
