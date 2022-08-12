#!/bin/bash
docker-compose up airflow-init
docker-compose up -d --no-deps --build airflow-webserver airflow-scheduler

