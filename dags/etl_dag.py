from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

from ingest import ingestor
# from clean import cleaner
# from stage import stager

default_args = {
    "owner": "narapady",
    "retries": 5,
    "retry_delay": timedelta(minutes=5)
    }
    
with DAG(
    default_args=default_args,
    dag_id="etl_dag_v3",
    description="Extract Transform Load Operation Dag",
    start_date=datetime(2022, 8, 6),
    schedule_interval= '@weekly'

    ) as dag:
        task1 = PythonOperator(
            task_id="Ingest",
            python_callable= ingestor.run
        )
        task1
        
