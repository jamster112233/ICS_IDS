#!/usr/bin/env bash
python RIMITM.py &> RIData.txt 2>&1 &
python RIMITMController.py
kill $(pidof python)
