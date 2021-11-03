#!/usr/bin/env python

import os
import sys
from pathlib import Path

from jinja2 import Template

BASE_DIR = Path(__file__).resolve().parent


def render_speaker():
    global BASE_DIR, SERVICES_PATH, USER

    speaker_service_name = 'speaker'
    with open(os.path.join(BASE_DIR, speaker_service_name + '.service')) as f:
        speaker_template = Template(f.read())

    context = {
        'working_directory': os.path.join(BASE_DIR.parent, 'src'),
        'user': USER,
        'python_env_path': os.path.join(BASE_DIR.parent, 'env', 'bin', 'python'),
        'script': os.path.join(BASE_DIR.parent, 'src', 'speaker.py'),
        'args': '-symd -log=info -in_func=rpi_button',
    }
    speaker = speaker_template.render(**context)

    with open(os.path.join(SERVICES_PATH, speaker_service_name + '.service'), 'w') as f:
        f.write(speaker)


def render_speaker_updater():
    global BASE_DIR, SERVICES_PATH, USER

    speaker_updater_service_name = 'speaker_updater'
    with open(os.path.join(BASE_DIR, speaker_updater_service_name + '.service')) as f:
        speaker_updater_template = Template(f.read())

    context = {
        'working_directory': os.path.join(BASE_DIR.parent, 'updater'),
        'user': USER,
        'python_env_path': os.path.join(BASE_DIR.parent, 'env', 'bin', 'python'),
        'script': os.path.join(BASE_DIR.parent, 'updater', 'update.py'),
        'args': '',
    }
    speaker_updater = speaker_updater_template.render(**context)

    with open(os.path.join(SERVICES_PATH, speaker_updater_service_name + '.service'), 'w') as f:
        f.write(speaker_updater)

    with open(os.path.join(BASE_DIR, speaker_updater_service_name + '.timer')) as f:
        speaker_updater_timer_template = Template(f.read())

    context = {
        'restart_time_s': str(60 * 60),
    }
    speaker_updater_timer = speaker_updater_timer_template.render(**context)

    with open(os.path.join(SERVICES_PATH, speaker_updater_service_name + '.timer'), 'w') as f:
        f.write(speaker_updater_timer)


def render_issue_manager():
    global BASE_DIR, SERVICES_PATH, USER

    issue_manager_service_name = 'speaker_issue_manager'
    with open(os.path.join(BASE_DIR, issue_manager_service_name + '.service')) as f:
        issue_manager_template = Template(f.read())

    context = {
        'working_directory': os.path.join(BASE_DIR.parent, 'issue_manager'),
        'user': USER,
        'python_env_path': os.path.join(BASE_DIR.parent, 'env', 'bin', 'python'),
        'script': os.path.join(BASE_DIR.parent, 'issue_manager', 'issue_manager.py'),
        'args': '',
    }
    issue_manager = issue_manager_template.render(**context)

    with open(os.path.join(SERVICES_PATH, issue_manager_service_name + '.service'), 'w') as f:
        f.write(issue_manager)


if __name__ == '__main__':
    _, USER, SERVICES_PATH = sys.argv
    render_speaker()
    render_speaker_updater()
    # render_issue_manager()
