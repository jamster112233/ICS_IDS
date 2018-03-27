#!/usr/bin/env bash
cmds=( "10.10.1.100"
       "10.10.1.101"
       "10.10.2.100"
       "10.10.2.101"
       "10.10.3.100"
       "10.10.3.101"
       "10.10.4.100"
       "10.10.4.101"
       "10.10.10.99"
       "10.10.10.100"
       "10.10.16.99"
       "10.10.255.254"
       "ns1.ics.example.com"
       "icsgw.ics.example.com"
       "enggw.ics.example.com"
       "ms.ics.example.com"
       "ria.ics.example.com"
       "cia.ics.example.com"
       "hmi.ics.example.com"
     )

for i in `seq 1 5000`;
do
    echo ==============
    echo [$i / 5000]
    echo ==============
    ping ${cmds[RANDOM % ${#cmds[@]}]} -c $(($RANDOM % 100))
    echo
done
