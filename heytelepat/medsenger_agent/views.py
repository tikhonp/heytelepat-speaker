from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
import json
from django.conf import settings
from medsenger_agent.models import Contract, Speaker, Message
from medsenger_agent import agent_api
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.core import exceptions

from rest_framework.views import APIView
from medsenger_agent import serializers
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.utils import timezone
import datetime


APP_KEY = settings.APP_KEY
DOMEN = settings.DOMEN
context = {
    'status': '400', 'reason': 'invalid key'
}
invalid_key_response = HttpResponse(
    json.dumps(context), content_type='application/json')
invalid_key_response.status_code = 400


@csrf_exempt
@require_http_methods(["POST"])
def init(request):
    data = json.loads(request.body)

    if data['api_key'] != APP_KEY:
        return invalid_key_response

    try:
        contract = Contract.objects.get(contract_id=data['contract_id'])
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


@csrf_exempt
@require_http_methods(["POST"])
def remove(request):
    data = json.loads(request.body)

    if data['api_key'] != APP_KEY:
        return invalid_key_response

    try:
        print(data['contract_id'])
        contract = Contract.objects.get(contract_id=data['contract_id'])
    except exceptions.ObjectDoesNotExist:
        response = HttpResponse(json.dumps({
            'status': 400, 'reason': 'there is no such object'
        }), content_type='application/json')
        response.status_code = 400
        return response

    contract.delete()

    return HttpResponse("ok")


@csrf_exempt
@require_http_methods(["POST"])
def status(request):
    data = json.loads(request.body)

    if data['api_key'] != APP_KEY:
        return invalid_key_response

    response = HttpResponse(json.dumps({
        'is_tracking_data': True,
        'supported_scenarios': [],
        'tracked_contracts': [i.contract_id for i in Contract.objects.all()]
    }), content_type="application/json")
    return response


@require_http_methods(["GET", "POST"])
def settings(request):
    if request.method == "GET":
        if request.GET.get('api_key', '') != APP_KEY:
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


@csrf_exempt
@require_http_methods(["GET", "POST"])
def newdevice(request):
    if request.method == "GET":
        if request.GET.get('api_key', '') != APP_KEY:
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

    if data['api_key'] != APP_KEY:
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


class IncomingMessageApiView(APIView):
    serializer_class = serializers.MessageSerializer

    def post(self, request):
        print(request.data)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            if serializer.data['api_key'] != APP_KEY:
                raise ValidationError(detail='Invalid token')

            try:
                contract = Contract.objects.get(
                    contract_id=serializer.data['contract_id'])
            except exceptions.ObjectDoesNotExist:
                raise ValidationError(detail='Contract does not exist')

            if serializer.data['message']['sender'] == 'patient':
                return HttpResponse("ok")
            date = serializer['message']['date']
            print(date, type(date))
            message = Message.objects.create(
                contract=contract,
                message_id=serializer.data['message']['id'],
                text=serializer.data['message']['text'],
                date=timezone.localtime(
                    datetime.datetime.strptime(
                        date,
                        "%Y-%m-%d %H:%M:%S").astimezone(timezone.utc)),
            )

            message.save()

            return HttpResponse("ok")

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
