#!/bin/bash

# To rebuild docker image, run
# docker build . --tag extending-airflow:lastest
docker-compose up airflow-init
docker-compose up -d --no-deps --build airflow-webserver airflow-scheduler

