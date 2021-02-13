import requests
from django.conf import settings


def send_message(contract_id, text, action_link=None, action_name=None,
                 action_onetime=False, action_big=False, only_doctor=False,
                 only_patient=False, action_deadline=None, is_urgent=False,
                 need_answer=False, attachments=None):

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
            settings.DOMEN + '/api/agents/order', json=data)
        print(response)
        answer = response.json()
        return int(answer['delivered']) / int(answer['receivers'])
    except Exception as e:
        print('Send_order connection error', e)
        return 0
