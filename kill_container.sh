#!/bin/bash

set -e

cd /home/ubuntu/carping/zip

docker-compose down
docker rm -f $(docker ps -a -q)