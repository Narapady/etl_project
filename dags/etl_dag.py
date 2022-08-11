from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.providers.snowflake.transfers.s3_to_snowflake import S3ToSnowflakeOperator

from ingest import ingestor
from transform import transformer
from stage import stager
from load import sql_command
from datetime import datetime, timedelta
from credential import ACCESS_KEY_ID, SECRET_ACCESS_KEY

DAG_ID = "ETL_DAG"
DATABASE = "us_food_nutrition"
SCHEMA = "public"
WAREHOUSE = "food_nutrition_wh"
SNOWFLAKE_CONN_ID = "snowflake_conn"
SNOWFLAKE_ROLE = "accountadmin"
S3_SNOWFLAKE_STAGE = "s3_stage"
STAGE_FILE_FORMAT = "csv_format"

CREATE_TABLE_CMD = sql_command.CREATE_TABLE_SQL
TABLE_MAP_DICT = sql_command.TABLE_MAP

default_args = {
    "owner": "narapady",
    "retries": 5,
    "retry_delay": timedelta(minutes=5)
    }
    
with DAG(
    default_args=default_args,
    dag_id=DAG_ID,
    description="Extract Transform Load Dag", 
    start_date=datetime(2022, 8, 6),
    schedule_interval= '@weekly'

) as dag:
    dummy = DummyOperator(task_id="Start")
    
    ingest = PythonOperator(
        task_id="Ingest_data_from_sources",
        python_callable=ingestor.run
    )

    transform = PythonOperator(
        task_id = "Transform_data",
        python_callable=transformer.run
    )

    stage = PythonOperator(
        task_id = "Stage_data",
        python_callable=stager.run
    )

    create_snowflake_tables = SnowflakeOperator(
        task_id='Create_snowflake_tables',
        sql=CREATE_TABLE_CMD,
        warehouse=WAREHOUSE,
        database=DATABASE,
        schema=SCHEMA,
        role=SNOWFLAKE_ROLE,
        snowflake_conn_id=SNOWFLAKE_CONN_ID
    )
    
    snowflake_load_jobs = []
    for table_name, filename in TABLE_MAP_DICT.items():
        load = S3ToSnowflakeOperator(
            task_id=f'Load_into_{table_name}_table',
            s3_keys=[filename],
            table=table_name,
            schema=SCHEMA,
            stage=S3_SNOWFLAKE_STAGE,
            file_format=STAGE_FILE_FORMAT,
            role=SNOWFLAKE_ROLE,
            snowflake_conn_id=SNOWFLAKE_CONN_ID
        )
        snowflake_load_jobs.append(load)
     
    dummy >> ingest >> transform >> stage >> create_snowflake_tables >> snowflake_load_jobs

        
