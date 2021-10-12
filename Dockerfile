# syntax = docker/dockerfile:1.2
# Dockerfile
# Django 최상위 루트에서 작성
FROM python:3.8-slim-buster
# 컨테이너 내에서 코드가 실행될 경로 설정
WORKDIR /usr/src/app
# requirements.txt에 명시된 필요한 packages 설치
COPY requirements.txt ./


RUN apt-get update && apt-get install gcc && apt-get install -y default-libmysqlclient-dev
RUN apt-get install python3-mysqldb  && apt-get install libssl-dev 

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Project를 /usr/src/app으로 복사
COPY . .
# 포트 설정
EXPOSE 8000
# gunicorn 실행
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "project_name.wsgi:application"]
