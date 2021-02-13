from django.http import HttpResponseServerError, HttpResponse
from django.views.decorators.http import require_http_methods
import json
from django.conf import settings
from medsenger_agent.models import Contract, Speaker
from medsenger_agent import agent_api
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.core import exceptions


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
            contract_id=data['contract_id']).save()

    agent_api.send_message(
        contract.contract_id,
        "Зарегистрируйте новое устройство",
        "/newdevice", "Добавить", only_patient=True, action_big=True)

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


def settings(request):
    return HttpResponseServerError()


def message(request):
    return HttpResponseServerError()


def action(request):
    return HttpResponseServerError()


@csrf_exempt
@require_http_methods(["GET", "POST"])
def newdevice(request):
    if request.method == "GET":
        if request.GET.get('api_key', '') != APP_KEY:
            return invalid_key_response

        return render(request, "newdevice.html", {
            "contract_id": request.GET.get('contract_id', ''),
            "Url": DOMEN+'/medsenger/newdevice/'})

    else:
        code = int(request.POST.get('code', 0))
        contract_id = int(request.POST.get('contract_id', ''))

        try:
            speaker = Speaker.objects.get(code=code)
        except exceptions.ObjectDoesNotExist:
            response = HttpResponse(json.dumps({
                'status': 400,
                'reason': 'Invalid code'
            }), content_type='application/json')
            response.status = 500
            return response

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

        return HttpResponse("ok")

    return HttpResponseServerError()
