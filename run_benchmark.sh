#!/bin/bash

source .venv/bin/activate
sudo .venv/bin/python3 src/benchmark/run_benchmarks.py $DEVICE_INDEX

sudo nvidia-smi -rgc
sudo nvidia-smi -rmc
