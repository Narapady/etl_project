
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
