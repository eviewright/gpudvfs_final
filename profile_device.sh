#!/bin/bash

source .venv/bin/activate
sudo .venv/bin/python3 src/device_profiler.py $DEVICE_INDEX $GL_PROP $ML_PROP
