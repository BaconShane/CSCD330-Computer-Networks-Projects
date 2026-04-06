#!/bin/bash

site1="http://google.com"
site2="http://httpforever.com"
site3="http://amazon.com"

echo $site1:
python3 ./lab4.py -p 80 $site1
echo
echo $site2:
python3 ./lab4.py -p 80 $site2
echo
echo $site3:
python3 ./lab4.py -p 80 $site3
echo
echo $site2: Printed to output.txt
python3 ./lab4.py -f 80 $site2