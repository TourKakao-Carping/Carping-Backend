#!/bin/bash

cd /home/ubuntu/carping/zip

docker rm -f $(docker ps -a -q)