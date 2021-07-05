#!/bin/sh
cd /home/pi/heytelepat/Speaker
source env/bin/activate
/home/pi/heytelepat/Speaker/env/bin/python speaker.py -log=info -infunc=rpibutton
