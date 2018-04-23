#!/usr/bin/env bash
python RIMITM.py &> RIData.txt &
python RIMITMController.py
kill $(pidof python)
