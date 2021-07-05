import requests
from django.conf import settings
import datetime
import json
from medsenger_agent.models import Task


def send_message(contract_id, text, action_link=None, action_name=None,
                 action_onetime=False, action_big=False, only_doctor=False,
                 only_patient=False, action_deadline=None, is_urgent=False,
                 need_answer=False, attachments=None, send_from='patient'):

    message = {
        "text": text
    }

    if action_link:
        message['action_link'] = action_link

    if action_name:
        message['action_name'] = action_name

    if action_big:
        message['action_big'] = action_big

    if action_onetime:
        message['action_onetime'] = action_onetime

    if only_doctor:
        message['only_doctor'] = only_doctor

    if need_answer:
        message['need_answer'] = need_answer

    if only_patient:
        message['only_patient'] = only_patient

    if action_deadline:
        message['action_deadline'] = action_deadline

    if is_urgent:
        message['is_urgent'] = is_urgent

    if send_from:
        message['send_from'] = send_from

    if attachments:
        message['attachments'] = []

        for attachment in attachments:
            message['attachments'].append({
                "name": attachment[0],
                "type": attachment[1],
                "base64": attachment[2],
            })

    data = {
        "contract_id": contract_id,
        "api_key": settings.APP_KEY,
        "message": message
    }

    try:
        url = settings.MAIN_HOST + '/api/agents/message'
        answer = requests.post(url, json=data)
        # print(answer, answer.text, url, data)
    except Exception as e:
        print('Sendmessage connection error', e)


def send_order(contract_id, order, receiver_id=None, params=None):
    data = {
        "contract_id": contract_id,
        "api_key": settings.APP_KEY,
        "order": order,
    }

    if receiver_id:
        data['receiver_id'] = receiver_id

    if params:
        data['params'] = params

    try:
        print("req data:\n", data)
        response = requests.post(
            settings.MAIN_HOST + '/api/agents/order', json=data)
        print(response)
        answer = response.json()
        return int(answer['delivered']) / int(answer['receivers'])
    except Exception as e:
        print('Send_order connection error', e)
        return 0


def check_insatce_task_measurement(task, data):
    task.alias = data['alias']
    task.unit = data['unit']

    # if data['mode'] == task.DAILY:
        # task.mode = task.DAILY
    # elif data['mode'] == task.WEEKLY:
        # task.mode = task.WEEKLY
    # else:
        # data['mode'] = task.MONTHLY

    task.last_push = datetime.datetime.strptime(
        data['last_push'], "%Y-%m-%d %H:%M:%S")
    task.show = data['show']

    if data['name'] == 'pressure':
        task.for_pressure_field = json.dumps({
            'max_systolic': data['max_systolic'],
            'min_systolic': data['min_systolic'],
            'max_diastolic': data['max_diastolic'],
            'min_diastolic': data['min_diastolic'],
            'max_pulse': data['max_pulse'],
            'min_pulse': data['min_pulse'],
        })
    else:
        task.max_value = data['max']
        task.min_value = data['min']

    return task


def get_instance(contract, name, mode, time):
    if mode == "daily":
        t = Task.objects.filter(
            contract=contract,
            name=name, mode=Task.DAILY,
            hours=time['value']
        )
        if len(t) == 0:
            t = Task.objects.create(
                contract=contract,
                name=name, mode=Task.DAILY,
                hours=time['value'],
            )
        else:
            t = t.first()
        return t
    elif mode == "weekly":
        t = Task.objects.filter(
            contract=contract,
            name=name, mode=Task.WEEKLY,
            days_week_day=time['day'],
            days_week_hour=time['hour'],
        )
        if len(t) == 0:
            t = Task.objects.create(
                contract=contract,
                name=name, mode=Task.WEEKLY,
                days_month_day=time['day'],
                days_month_hour=time['hour'],
            )
        else:
            t = t.first()
        return t
    else:
        t = Task.objects.filter(
            contract=contract,
            name=name, mode=Task.MONTHLY,
            days_month_day=time['day'],
            days_month_hour=time['hour'],
        )
        if len(t) == 0:
            t = Task.objects.create(
                contract=contract,
                name=name, mode=Task.MONTHLY,
                days_month_day=time['day'],
                days_month_hour=time['hour'],
            )
        else:
            t = t.first()
        return t


def add_record(contract_id, category_name, value, record_time=None):
    data = {
        "contract_id": contract_id,
        "api_key": settings.APP_KEY,
        "category_name": category_name,
        "value": value,
    }

    if record_time:
        data['time'] = record_time

    try:
        _ = requests.post(
            settings.MAIN_HOST + '/api/agents/records/add', json=data)
    except Exception as e:
        print('connection error', e)


def add_records(contract_id, values, record_time=None):
    """values: [(category_name, value)]"""
    data = {
        "contract_id": contract_id,
        "api_key": settings.APP_KEY,
    }

    if record_time:
        data['values'] = [{
            "category_name": category_name,
            "value": value,
            "time": record_time
        } for (category_name, value) in values]
    else:
        data['values'] = [{
            "category_name": category_name,
            "value": value} for (category_name, value) in values]
    try:
        requests.post(
            settings.MAIN_HOST + '/api/agents/records/add', json=data)
    except Exception as e:
        print('connection error', e)


def get_list_categories():
    answer = requests.get(
        settings.MAIN_HOST + '/api/agents/records/categories',
        json={'api_key': settings.APP_KEY})

    if answer.status_code != 200:
        raise RuntimeError("Error with get list categories")

    return answer.json()
