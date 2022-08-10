from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

from ingest import ingestor
from transform import transformer
from stage import stager

default_args = {
    "owner": "narapady",
    "retries": 5,
    "retry_delay": timedelta(minutes=5)
    }
    
with DAG(
    default_args=default_args,
    dag_id="ETL_DAG",
    description="Extract Transform Load Operation Dag",
    start_date=datetime(2022, 8, 6),
    schedule_interval= '@weekly'

) as dag:
    ingest = PythonOperator(
        task_id="Ingestor",
        python_callable=ingestor.run
    )

    transform = PythonOperator(
        task_id = "Transformer",
        python_callable=transformer.run
    )
    
    stage = PythonOperator(
        task_id = "Stager",
        python_callable=stager.run
    )
    
    ingest >> transform >> stage   

        
