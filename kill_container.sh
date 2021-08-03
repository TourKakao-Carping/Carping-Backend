#!/bin/bash

set -e

docker-compose down
docker rm -f $(docker ps -a -q)