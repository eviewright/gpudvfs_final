#!/bin/bash

source .venv/bin/activate
.venv/bin/python3 src/benchmark/calculate_average.py $DEVICE_INDEX
