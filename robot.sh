#!/usr/bin/bash
PROJ_PATH=/home/pi/dyplom
cd $PROJ_PATH/frontend/build
fuser -k 8080/tcp
fuser -k 8081/tcp
fuser -k 8000/tcp
fuser -k 5000/tcp
PYTHON=/home/pi/dyplom/venv2/bin/python
trap 'kill 0' SIGINT
cd $PROJ_PATH/motor-service && $PYTHON main.py &
cd $PROJ_PATH/camera-service && $PYTHON main.py &
cd $PROJ_PATH && $PYTHON -m gunicorn -b 127.0.0.1:5000 'app:app'
wait
