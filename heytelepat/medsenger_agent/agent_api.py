from medsenger_agent.models import Task
import datetime
import json


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
