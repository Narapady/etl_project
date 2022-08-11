import os
import requests
import zipfile
from bs4 import BeautifulSoup
from storage.s3 import S3AWS 
from ingest.source import USDA_URL
from credential import ACCESS_KEY_ID, SECRET_ACCESS_KEY

def to_lowercase(word: str):
    """
    Convert title to all lowercase delimited by "-"
    """
    result = word.split(" ")
    result = [item.lower() for item in result]
    return " ".join(result).replace(" ", "-")

def get_links(url: str): 
    """
    Fetch the download links and group titles for each dataset from usda.
    returns a dictionary in form of {"group title": list of download links 
    corresponding to the group title}. This is used as helper function when
    ingesting data from usda to S3
    """
    base_url = url[:url.find("v") + 1]
    req = requests.get(url)
    soup = BeautifulSoup(req.content, features="html.parser")
    table_rows = soup.find_all("tr")
    links = {}
    for row in table_rows:
        table_data = row.find_all("td")
        for item in table_data:
            title = item.find("strong")
            if title and title not in links and "Archived" not in title.text:
                links[title.text] = []
                continue
            link = item.find("a")
            if link:
                links[list(links.keys())[-1]].append(base_url + link["href"])
 
    return links

def filter_links(source_list):
    new_dict = {}
    for dict_ in source_list:
        for key, value in dict_.items():
           new_dict[key] = value 
           
    del new_dict["2006"]
    del new_dict["2007"]
    del new_dict["Food Availability"]
    del new_dict["Food at Home and Food Away from Home"]
    del new_dict["Demographic and Socioeconomic Characteristics"]

    return new_dict
def ingest_usda(s3, sources, bucket_name, category):
    """
    Ingest data from USDA ERS to specified S3 buckets. 'sources' paramenter
    is the website links that contain data to ingest. 
    """
    source_list = [get_links(source) for source in sources]
    links = filter_links(source_list)[category]    
    key = to_lowercase(category)        
    
    for link in links:
        req = requests.get(link)
        filename = req.url[link.rfind("/") + 1: link.rfind("?")]
        load_to_s3 = s3.s3_client().put_object( 
                        Bucket= bucket_name,
                        Body= req.content,
                        Key=  key + "/" + filename
                    )
        if load_to_s3:
            print(f"Successfully uploaded {key}/{filename} to {bucket_name}")
        else:
            print(f"Failed to upload {key}/{filename} to {bucket_name}")

def ingest_kaggle(s3, sources, bucket_name):
    """
    Ingest data from Kaggle to specified S3 bucket via Kaggle API commnads.
    'sources' paramenter is a list of kaggle api commands to get the data. 
    """
    for api_command in sources:
        os.system(api_command)
        filename = api_command.split("/")[1]
        with zipfile.ZipFile(filename + ".zip") as zip:
            zip.extractall()
            for file in os.listdir():
                if ".csv" in file:
                    s3.s3_client().upload_file(file, bucket_name, "obesity/" + file)
                    print(f"Successfully uploaded {file} to {bucket_name}")
            
    os.system("rm *.zip *.csv")
    
def create_s3_bucket_raw(bucket_name):
    s3 = S3AWS(ACCESS_KEY_ID, SECRET_ACCESS_KEY)
    return s3.create_bucket(bucket_name)

class Ingestor:
    """
    Ingestor class is repsonsible for ingesting data from source system with
    instance method ingest() to ingest data from source systems to aws object storage s3.
    The instantiation takes s3 object, s3's bucket name to load data to, and list of source links/api commands
    """
    def __init__(self, s3, source, bucket_name, category):
        self.s3 = s3
        self.bucket_name = bucket_name 
        self.source = source
        self.category = category
        
    def ingest(self):
        """
        ingesting data to s3 bucket based on ingesting strategy
        """
        # ingest_kaggle(self.s3, self.kaggle_sources, self.bucket_name)
        ingest_usda(self.s3, self.source, self.bucket_name, self.category)
            
def run(category):
    """
    Main function of ingestion program. One aws s3 is instantiated, and
    ingest data from 2 sources systems including data from usda and kaggle. 
    Data will land in S3 with specified bucket names. 
    """
    
    s3 = S3AWS(ACCESS_KEY_ID, SECRET_ACCESS_KEY)
    # kaggle = s3.create_bucket("s3-bucket-raw-kaggle") 
    # usda = s3.create_bucket("s3-bucket-raw-usda") 
    
    # ingestor_kaggle = Ingestor(s3, kaggle_sources, "s3-bucket-raw-kaggle")
    # ingestor_kaggle.ingest("ingest_kaggle")

    ingestor_usda = Ingestor(s3, USDA_URL, "s3-bucket-raw-usda", category)
    ingestor_usda.ingest()

USDA_LIST = [
        "Loss-Adjusted Food Availability",
        "Food Consumption Estimates",
        "Nutrient Intake Estimates",
        "2016",
        "2015",
        "2014",
        "Consumer Price Index",
        "Producer Price Index",
        "Current Food Expenditure Series"
        ]
