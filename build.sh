#!/bin/sh
cd /home/data/code
cp /etc/hosts ./hosts.txt
docker build -t ty-server .