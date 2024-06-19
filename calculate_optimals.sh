#!/bin/bash

source .venv/bin/activate

if [ $USE_AVERAGES == 1 ]
then
    .venv/bin/python3 src/benchmark/calculate_optimals.py $DEVICE_INDEX --average
else
    .venv/bin/python3 src/benchmark/calculate_optimals.py $DEVICE_INDEX
fi