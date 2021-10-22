#!/bin/bash
cd /home/ubuntu/carping/zip/

docker-compose up --build -d

docker rmi $(docker images -f "dangling=true" -q)