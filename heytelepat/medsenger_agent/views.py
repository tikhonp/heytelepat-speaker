from django.http import HttpResponseServerError, HttpResponse, \
    HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
import json
from django.conf import settings
from medsenger_agent.models import Contract, Speaker
from medsenger_agent import agent_api
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.core import exceptions

from django.http import HttpResponse
from medsenger_agent.models import Speaker, Task
from rest_framework import generics
from medsenger_agent import serializers
from django.core import exceptions
from rest_framework.exceptions import ValidationError, NotFound
from medsenger_agent import agent_api
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

context = {
    'status': '400', 'reason': 'invalid key'
}
invalid_key_response = HttpResponse(
    json.dumps(context), content_type='application/json')
invalid_key_response.status_code = 400


class InitApiView(APIView):
    serializer_class = serializers.InitSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            try:
                contract = Contract.objects.get(
                    contract_id=data['contract_id'])
            except exceptions.ObjectDoesNotExist:
                contract = Contract.objects.create(
                    contract_id=data['contract_id'])
                contract.save()

            agent_api.send_message(
                contract.contract_id,
                "Зарегистрируйте новое устройство",
                "newdevice", "Добавить", only_patient=True, action_big=True)

            agent_api.send_order(contract.contract_id, 'get_settings',  12)

            return HttpResponse("ok")

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RemoveApiView(APIView):
    serializer_class = serializers.MedsengerGenericSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            try:
                contract = Contract.objects.get(
                    contract_id=data['contract_id'])
            except exceptions.ObjectDoesNotExist:
                raise NotFound("Contract with those is not found")

            contract.delete()
            return HttpResponse("ok")

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StatusApiView(APIView):
    serializer_class = serializers.StatusSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            context = {
                'is_tracking_data': True,
                'supported_scenarios': [],
                'tracked_contracts': [
                    i.contract_id for i in Contract.objects.all()]
            }

            return Response(context)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@require_http_methods(["GET", "POST"])
def settingsAPI(request):
    if request.method == "GET":
        if request.GET.get('api_key', '') != settings.APP_KEY:
            return invalid_key_response

        contract_id = request.GET.get('contract_id', '')

    else:
        s_id = request.POST.get('speaker_id', '')
        contract_id = request.POST.get('contract_id', '')

        speaker = Speaker.objects.get(pk=s_id)
        speaker.delete()

    speakers = Speaker.objects.filter(contract=Contract.objects.get(
            contract_id=contract_id))

    return render(request, "settings.html", {
            "contract_id": contract_id,
            "speakers": speakers,
            "api_key": request.GET.get('api_key', ''),
            "len_speakers": len(speakers),
        })


class MessageApiView(APIView):
    serializer_class = serializers.MessageApiSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return HttpResponse("ok")

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def newdevice(request):
    if request.method == "GET":
        if request.GET.get('api_key', '') != settings.APP_KEY:
            return invalid_key_response

        return render(request, "newdevice.html", {
            "contract_id": request.GET.get('contract_id', ''),
        })

    else:
        code = int(request.POST.get('code', 0))
        contract_id = int(request.POST.get('contract_id', ''))

        try:
            speaker = Speaker.objects.get(code=code)
        except exceptions.ObjectDoesNotExist:
            return render(request, "newdevice.html", {
                "contract_id": contract_id,
                "invalid_code": True,
                "value": code,
            })

        try:
            contract = Contract.objects.get(contract_id=contract_id)
        except exceptions.ObjectDoesNotExist:
            response = HttpResponse(json.dumps({
                'status': 500,
                'reason': 'Contract doesnot exist please reconnect agent',
            }), content_type='application/json')
            response.status_code = 500
            return response

        speaker.contract = contract
        speaker.save()

        return render(request, 'done_add_device.html')


@csrf_exempt
@require_http_methods(["POST"])
def order(request):
    data = json.loads(request.body)
    print(data)

    if data['api_key'] != settings.APP_KEY:
        return invalid_key_response

    try:
        contract = Contract.objects.get(contract_id=data['contract_id'])
    except exceptions.ObjectDoesNotExist:
        response = HttpResponse(json.dumps({
            'status': 400,
            'reason': 'COntract_id does not exist, add agent to this chat'
        }), content_type='application/json')
        response.status_code = 400
        return response

    for measurement in data['params']['measurements']:
        time = None
        if measurement['mode'] == 'daily':
            time = measurement['timetable'][0]['hours']
        elif measurement['mode'] == 'weekly':
            time = measurement['timetable'][0]['days_week']
        else:
            time = measurement['timetable'][0]['days_month']

        for t in time:
            instance = agent_api.get_instance(
                contract,
                measurement['name'],
                measurement['mode'],
                t
            )
            instance = agent_api.check_insatce_task_measurement(
                instance, measurement)
            instance.save()

    return HttpResponse("ok")
