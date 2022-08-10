create or replace storage integration s3_integration
  type = external_stage
  storage_provider = s3
  enabled = true
  storage_aws_role_arn = 'arn:aws:iam::<arn number>:role/snowflake_role'
  storage_allowed_locations = ('s3://s3-bucket-staged/', 's3://s3-bucket-staged/');
  
DESC INTEGRATION s3_integration;
  
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
