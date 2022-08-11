from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime, timedelta
# from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.providers.snowflake.transfers.s3_to_snowflake import S3ToSnowflakeOperator

from ingest import ingestor
from transform import transformer
from stage import stager
from storage import s3
from credential import ACCESS_KEY_ID, SECRET_ACCESS_KEY

default_args = {
    "owner": "narapady",
    "retries": 5,
    "retry_delay": timedelta(minutes=5)
    }
    
with DAG(
    default_args=default_args,
    dag_id="ETL_DAG_V6",
    description="Extract Transform Load Operation Dag",
    start_date=datetime(2022, 8, 6),
    schedule_interval= '@weekly'

) as dag:
    dummy = DummyOperator(task_id="Start")
    # ingest = PythonOperator(
    #     task_id="Ingest_data_from_sources",
    #     python_callable=ingestor.run
    # )
    #
    # transform = PythonOperator(
    #     task_id = "Transform_and_clean_data",
    #     python_callable=transformer.run
    # )
    # 
    # stage = PythonOperator(
    #     task_id = "Stage_data",
    #     python_callable=stager.run
    # )
    
    table_file_map = {
            "obesity_gdp": "Obesity_GDP_PanelData-staged.csv",
            "fast_food": "fast-food-staged.csv",
            "food_consumption_estimates": "food-consumption-estimates-staged.csv",
            "food_expenditure": "food-expenditure-staged.csv",
            "daily_food_availability": "loss-adjusted-food-availability-staged.csv",
            "monthly_sales": "monthly-sales-staged.csv",
            "nutrient_intake_estimates": "nutrient-intake-estimates-staged.csv",
            "obesity_world": "obesity-staged.csv",
            "food_availability_percent": "percents-staged.csv",
            "price_index": "price-index-staged.csv",
            "food_availability_calories": "totals-staged.csv",
            }
    snowflake_job = []
    for table_name, filename in table_file_map.items():
        load = S3ToSnowflakeOperator(
            task_id=f'load_into_{table_name}',
            s3_keys=[filename],
            table=table_name,
            schema='public',
            stage='s3_stage',
            file_format="csv_format",
            role="accountadmin",
            snowflake_conn_id="snowflake_conn"
        )
        snowflake_job.append(load)
     
    # ingest >> transform >> stage >> load  
    dummy >> snowflake_job

        
