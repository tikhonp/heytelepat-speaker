import requests
from django.conf import settings


def send_message(contract_id, text, action_link=None, action_name=None, action_onetime=True, action_big=False, only_doctor=False,
                 only_patient=False, action_deadline=None, is_urgent=False, need_answer=False,
                 attachments=None):
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
        print(answer, answer.text, url)
    except Exception as e:
        print('connection error', e)
