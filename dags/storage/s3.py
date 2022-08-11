import boto3
import os
import pandas as pd
from smart_open import smart_open
from typing import Optional
from io import BytesIO
class S3AWS:
    """
    S3AWS represents aws object storage s3. It handles necessary features including
    authenticating to access to s3, and creating bucket to store the ingested data
    """
    def __init__(self, access_key_id: Optional[str], secret_key_id: Optional[str]):
        self.access_key_id = access_key_id
        self.secret_key_id = secret_key_id
        self.client = boto3.client('s3', 
                           aws_access_key_id=self.access_key_id,
                           aws_secret_access_key=self.secret_key_id)

    def s3_client(self):
        return self.client
    
    def create_bucket(self, bucket_name: str):
        """
        Create S3 bucket with bucket_name
        """
        return self.client.create_bucket(Bucket=bucket_name)

    def load_df(self, bucket_name: str, key: str, type: str, sheet=0) -> pd.DataFrame:
        path = f"s3://{self.access_key_id}:{self.secret_key_id}@{bucket_name}/{key}"
        if type == "csv":
            return pd.read_csv(smart_open(path))
        elif type == "xls" or type == 'xlsx':
            return pd.read_excel(smart_open(path), sheet)

        
    def df_to_s3(self, dataframe: pd.DataFrame, bucket_name: str, key: str) -> None:
        
        return self.client.put_object(
                Bucket=bucket_name,
                Body=dataframe.to_csv(None).encode(),
                Key=key)

    def list_files(self, bucket_name: str, dirname: str):
        response =self.client.list_objects_v2(Bucket=bucket_name, Prefix=dirname)
        files = response.get("Contents")
    
        return [file['Key'].split("/")[1] for file in files]

    def get_sheetnames(self, bucket_name: str, key: str):
        s3_file = BytesIO()
        self.client.download_fileobj(bucket_name, key, s3_file)
        return pd.ExcelFile(s3_file).sheet_names



