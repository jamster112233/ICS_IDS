#!/usr/bin/env bash

cmds=( "10.10.1.101"
       "10.10.2.101"
       "10.10.3.101"
       "10.10.4.101"
       "10.10.10.100"
       "ms.ics.example.com"
       "ria.ics.example.com"
       "cia.ics.example.com"
       "hmi.ics.example.com"
     )

for i in `seq 1 300`;
do
    ./sshAuto.expect ${cmds[RANDOM % ${#cmds[@]}]}
done
