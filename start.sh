#!/bin/bash
# start.sh — one-command start
cd "$(dirname "$0")"
export PYTHONPATH=.
python3 main.py
