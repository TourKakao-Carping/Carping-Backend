#!/bin/bash
cd /home/ubuntu/carping/zip/

docker-compose up --build -d

NONE_CHECK = $(docker images -f "dangling=true" -q)

if [ -z ${NONE_CHECK} ]
then
    echo "Not Found None iamge"
else    
    docker rmi ${NONE_CHECK}
fi


