#!/usr/bin/bash
PROJ_PATH=/home/jordan/studia/dyplom/robot-control
cd $PROJ_PATH/frontend/build
fuser -k 8080/tcp
fuser -k 8081/tcp
fuser -k 8000/tcp
fuser -k 3000/tcp
PYTHON=/home/jordan/studia/dyplom/robot-control/venv/bin/python
trap 'kill 0' SIGINT
$PYTHON -m http.server 3000 &
cd $PROJ_PATH/motor-service && $PYTHON main.py &
cd $PROJ_PATH/camera-service && $PYTHON test.py &
cd $PROJ_PATH && $PYTHON app.py
wait