#!/bin/bash

NAME="seng3011"                              #Name of the application (*)
DJANGODIR=/home/zhilu/epiwatchAPI 		# Django project directory (*)
SOCKFILE=/home/zhilu/epiwatchAPI/run/gunicorn.sock        # we will communicate using this unix socket (*)
USER=nginx                                        # the user to run as (*)
GROUP=webdata                                     # the group to run as (*)
NUM_WORKERS=3                                     # how many worker processes should Gunicorn spawn (*)
DJANGO_SETTINGS_MODULE=seng3011.settings             # which settings file should Django use (*)
DJANGO_WSGI_MODULE=seng3011.wsgi                     # WSGI module name (*)

echo "Starting $NAME as `whoami`"

# Activate the virtual environment
cd $DJANGODIR
source /home/zhilu/epiwatchAPI/env/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec /home/zhilu/epiwatchAPI/env/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --bind=unix:$SOCKFILE
