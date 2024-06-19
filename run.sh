#!/bin/bash

source .venv/bin/activate

if [[ $USE_AVERAGES == 1 && $RUN_TEMP == 1 ]];
then
    sudo .venv/bin/python3 src/gpu_dvfs.py $DEVICE_INDEX --usetemperature --average
elif [[ $USE_AVERAGES == 1 ]];
then
    sudo .venv/bin/python3 src/gpu_dvfs.py $DEVICE_INDEX --average
elif [[ $RUN_TEMP == 1 ]];
then
    sudo .venv/bin/python3 src/gpu_dvfs.py $DEVICE_INDEX --usetemperature
else
    sudo .venv/bin/python3 src/gpu_dvfs.py $DEVICE_INDEX
fi