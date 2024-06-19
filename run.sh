#!/bin/bash

source .venv/bin/activate
sudo .venv/bin/python3 src/gpu_dvfs.py $DEVICE_INDEX
