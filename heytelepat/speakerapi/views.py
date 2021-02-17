from django.http import HttpResponse
from medsenger_agent.models import Speaker, Task
from rest_framework import generics
from speakerapi import serializers
from django.core import exceptions
from rest_framework.exceptions import ValidationError
from medsenger_agent import agent_api
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class SpeakerInitApiView(APIView):
    def post(self, request, format=None):
        speaker = Speaker.objects.create()
        speaker.save()

        context = {
            'code': speaker.code,
            'token': speaker.token
        }

        return Response(context)


class SpeakerDeleteApiView(APIView):
    def delete(self, request, format=None):
        token = self.request.data.get('token', '')
        try:
            s = Speaker.objects.get(token=token)
        except exceptions.ObjectDoesNotExist:
            raise ValidationError(detail='Invalid Token')
        s.delete()
        return HttpResponse('OK')


class TaskApiView(generics.ListAPIView):
    serializer_class = serializers.TaskSerializer

    def get_queryset(self):
        token = self.request.data.get('token', '')
        try:
            s = Speaker.objects.get(token=token)
            queryset = Task.objects.filter(contract=s.contract)
            return queryset
        except exceptions.ObjectDoesNotExist:
            raise ValidationError(detail='Invalid Token')

    def patch(self, request):
        task_id = self.request.data.get('task_id', '')
        try:
            task = Task.objects.get(pk=int(task_id))
            task.is_done = True
            task.save()
            return HttpResponse("ok")
        except exceptions.ObjectDoesNotExist:
            raise ValidationError(detail='Invalid ID')


class SendMessageApiView(APIView):
    serializer_class = serializers.CommentSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            message = serializer.data['message']
            token = serializer.data['token']

            try:
                s = Speaker.objects.get(token=token)
            except exceptions.ObjectDoesNotExist:
                raise ValidationError(detail='Invalid Token')

            agent_api.send_message(s.contract.contract_id, message)
            return HttpResponse('OK')

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendValueApiView(APIView):
    serializer_class = serializers.SendValueSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            data = serializer.data['data']
            token = serializer.data['token']

            try:
                s = Speaker.objects.get(token=token)
            except exceptions.ObjectDoesNotExist:
                raise ValidationError(detail='Invalid Token')

            if len(data) == 1:
                agent_api.add_record(
                    s.contract.contract_id,
                    data[0]['category_name'],
                    data[0]['value'],
                )
            else:
                agent_api.add_records(
                    s.contract.contract_id,
                    data
                )

            return HttpResponse('OK')

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
