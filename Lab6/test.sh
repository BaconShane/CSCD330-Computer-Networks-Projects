#!/bin/bash

site1="http://httpforever.com"
site2="http://google.com"

sudo iptables -I OUTPUT -p tcp --tcp-flags ALL RST -j DROP

sudo python3 ./lab6.py $site1

sudo python3 ./lab6.py $site2

sudo iptables -D OUTPUT -p tcp --tcp-flags ALL RST -j DROP