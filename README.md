# PROJECT OVERVIEW
A data engineering project, specifically an automated data pipeline that weekly ingests US food and nutrition data from source systems to a data lake on S3. Then, it transforms, cleans, stages, and loads the data into a data warehouse, Snowflake. Finally, it builds a dashboard in Superset.


## Development and Framework
Using Apache Airflow as the pipeline orchestrator and running in containers via Docker and Docker Compose.
Cloud-based storage and visualization tools: AWS S3, Snowflake, and Preset.

## Data sources
#### US Department of Agriculture, Economic Research Service
- [US Food Availibility](https://www.ers.usda.gov/data-products/food-availability-per-capita-data-system/)
- [US Food Consumption and Nutrient Intakes](https://www.ers.usda.gov/data-products/food-consumption-and-nutrient-intakes/)
- [US Eating and Health Module](https://www.ers.usda.gov/data-products/eating-and-health-module-atus/)
- [US Food Price Outlook](https://www.ers.usda.gov/data-products/food-price-outlook/)
- [US Food Expenditure Series](https://www.ers.usda.gov/data-products/food-expenditure-series/)

#### Obesity Data (Kaggle) 
- [Obesity among adults by country, 1975 - 2016](https://www.kaggle.com/datasets/amanarora/obesity-among-adults-by-country-19752016)
- [Obesity and GDP US (2014-2017)](https://www.kaggle.com/datasets/annedunn/obesity-and-gdp-rates-from-50-states-in-20142017)
## To start Airflow:
```
docker build . --tag extending-airflow:lastest
docker-compose up airflow-init
docker-compose up -d --no-deps --build airflow-webserver airflow-scheduler
```
## To shutdown Airflow:
```
docker-compose down
```

## Tech Stack
![title](images/project_architecture.png)

## Airflow DAG
![title](images/airflow_dag.png)

## Interactive Dashbord in Superset
![title](images/d1.png)
![title](images/d2.png)
![title](images/d3.png)
![title](images/d4.png)
![title](images/d5.png)
![title](images/d6.png)
![title](images/d7.png)
![title](images/d8.png)



