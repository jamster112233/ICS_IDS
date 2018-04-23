#!/usr/bin/env bash
python CIMITM.py > CIData.txt 2>&1 &
python CIMITMController.py
kill $(pidof python)
