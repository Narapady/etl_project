-- Stage in snowflake represents the data sources from both
-- internal and external of Snowflake. In this case, we use external
-- data storage source, S3. After stage has been created we can load
-- data into snowflake tables.

-- Establish Integration between Amazon S3 and Snowflake
create or replace storage integration s3_integration
  type = external_stage
  storage_provider = s3
  enabled = true
  storage_aws_role_arn = 'arn:aws:iam::<arn number>:role/snowflake_role'
  storage_allowed_locations = ('s3://s3-bucket-staged/', 's3://s3-bucket-staged/');
  
DESC INTEGRATION s3_integration;

-- Create file format for the stage
create or replace file format csv_format
    type = 'CSV'
    record_delimiter = "\n"
    field_delimiter = ','
    skip_header = 1
    empty_field_as_null = true
    FIELD_OPTIONALLY_ENCLOSED_BY = '0x22'
    
create or replace stage s3_stage
    storage_integration = s3_integration
    url = 's3://s3-bucket-staged/'
    file_format = csv_format;
    
show stages; 
-- Create database and data warehouse
create or replace database us_food_nutrition;
use database us_food_nutrition;
use schema us_food_nutrition.public;

create or replace warehouse food_nutrition_wh with
  warehouse_size='X-SMALL'
  auto_suspend = 180
  auto_resume = true
  initially_suspended=true;

use warehouse food_nutrition_wh;
select current_warehouse();

-- Integrate with Preset for visulization
create network policy PRESET_WHITELIST
ALLOWED_IP_LIST = ('44.193.153.196', '52.70.123.52', '54.83.88.93');

