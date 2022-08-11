
"""
Heart of the program. This is Extract Transform Load DAG (Directed acyclic Graph).
There are 3 main operators used to process data pipeline:
     - Python Operator: used for ingestion, transformation, and staging
     - Snowflake Operator: used to interact with Snowflake API, creating talbes ...etc
     - S3ToSnowflakeOperator: used for S3 and snowflake integration for loading data
       from exteral storage (S3) to Snowflake

Data Pipeline Information:
     - Airflow Dag is run in docker-compose (multi-containers)
     - Data pipeline is scheduled to run weekly
     - Starting date of the data pipeline is August, 6, 2022
     - Computationally intensive tasks are run in parallel (ingest, tranform, stage)
Flow of Data Pipeline:
    (
    start_etl 
    >> ingest_s3_bucket >> ingest_jobs                  ## create s3 bucket to store raw data then ingest into it
    >> transform_s3_bucket >> transform_jobs            ## create s3 bucket to store transformed data then load into it 
    >> stage_s3_bucket >> stage_jobs                    ## create s3 bucket to store stageing data then load into it
    >> create_snowflake_tables >> snowflake_load_jobs   ## create target tables in snowflake then load data into correpsonding tables
    )
"""

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

# parameter for connecting to snowflake
DAG_ID = "ETL_DAG_V8"
DATABASE = "us_food_nutrition"
SCHEMA = "public"
WAREHOUSE = "food_nutrition_wh"
SNOWFLAKE_CONN_ID = "snowflake_conn"
SNOWFLAKE_ROLE = "accountadmin"
S3_SNOWFLAKE_STAGE = "s3_stage"
STAGE_FILE_FORMAT = "csv_format"
CREATE_TABLE_CMD = sql_command.CREATE_TABLE_SQL
TABLE_MAP_DICT = sql_command.TABLE_MAP

# list of dynamic python dags for ingest, transform, and load
INGEST_LIST  = ingestor.USDA_INGEST_LIST
TRANSFORM_LIST = transformer.USDA_TRANSFORM_LIST
STAGE_LIST = stager.STAGING_LIST

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
    # start the dag
    start_etl = DummyOperator(task_id="Start_ETL")
    
    # create s3 bucket for raw data
    ingest_s3_bucket = PythonOperator(
        task_id = "Create_s3_bucket_ingest",
        python_callable=ingestor.create_s3_bucket_ingest,
        op_kwargs={"bucket_name":"s3-bucket-raw-usda"}
    )
    
    # ingest jobs than run in parallel
    ingest_jobs = []
    for source in INGEST_LIST:
        source_category = source.lower().replace(" ", "_")
        ingest = PythonOperator(
            task_id=f"Ingest_from_{source_category}",
            python_callable=ingestor.run,
            op_kwargs={"category":source}
        )
        ingest_jobs.append(ingest)

    # create s3 bucket for transformed data
    transform_s3_bucket = PythonOperator(
        task_id = "Create_s3_bucket_transform",
        python_callable=transformer.create_s3_bucket_transform,
        op_kwargs={"bucket_name":"s3-bucket-clean-usda"}
    )
    
    # transform jobs than run in parallel
    transform_jobs = []
    for source in TRANSFORM_LIST:
        transform = PythonOperator(
            task_id=f"Transform_{source}",
            python_callable=transformer.run,
            op_kwargs={"category":source}
        )
        transform_jobs.append(transform)
        
    # create s3 bucket for staging data
    stage_s3_bucket = PythonOperator(
        task_id = "Create_s3_bucket_stage",
        python_callable=stager.create_s3_bucket_stage,
        op_kwargs={"bucket_name":"s3-bucket-staged"}
    )
    
    # stage jobs than run in parallel
    stage_jobs = []
    for source in list(STAGE_LIST.keys()):
        stage = PythonOperator(
            task_id=f"Stage_{source}",
            python_callable=stager.run,
            op_kwargs={"category":source}
        )
        stage_jobs.append(stage)

    # create tables in Snowflake
    create_snowflake_tables = SnowflakeOperator(
        task_id='Create_snowflake_tables',
        sql=CREATE_TABLE_CMD,
        warehouse=WAREHOUSE,
        database=DATABASE,
        schema=SCHEMA,
        role=SNOWFLAKE_ROLE,
        snowflake_conn_id=SNOWFLAKE_CONN_ID
    )
    
    # load to snowflake tables in parallel
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
    
    # Flow and order of data pipeline
    (
        start_etl 
        >> ingest_s3_bucket >> ingest_jobs
        >> transform_s3_bucket >> transform_jobs 
        >> stage_s3_bucket >> stage_jobs
        >> create_snowflake_tables >> snowflake_load_jobs
    )
        
