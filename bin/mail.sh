#!/bin/sh

cat /home/libor_rate/bin/email.txt | mail -s "$1" $2
