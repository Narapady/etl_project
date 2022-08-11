import pandas as pd 
import numpy as np
from storage.s3 import S3AWS
from credential import ACCESS_KEY_ID, SECRET_ACCESS_KEY, US_STATE_CODE


def load_to_S3(s3: S3AWS, df: pd.DataFrame, des_bucket: str, src_dir: str):
    """ load csv file to s3 specified s3 bucket and directory name"""
    
    df = df.reset_index(drop=True)
    key = src_dir.split("clean")[0][:-1] + "-staged.csv"
    load_to_s3 = s3.df_to_s3(df, des_bucket, key)
    if load_to_s3:
        print(f"Successfully loaded {key} to {des_bucket}")
        return True
    
    print(f"Failed to load {key} to {des_bucket}")
    return False

def stage_fastfood(s3: S3AWS, dirname: str, src_bucket: str = "s3-bucket-clean-usda", des_bucket: str = "s3-bucket-staged"):
    """ stage fast food data before loading to snowflake"""
    
    filenames = s3.list_files(src_bucket, dirname)
    result_df = pd.DataFrame()

    for file in filenames:
        df = s3.load_df(src_bucket, f"{dirname}/{file}", "csv")
        age_group = file.split(".")[0][:-5]
        year = file.split(".")[0][-4:]
        df['year'] = year
        df['age-group'] = age_group
        result_df = pd.concat([result_df, df])
        
    result_df = result_df.drop('Unnamed: 0', axis=1)
    return load_to_S3(s3, result_df, des_bucket, dirname)

def stage_foodnutrient_estimates(s3: S3AWS, dirname: str, src_bucket: str = "s3-bucket-clean-usda", des_bucket: str = "s3-bucket-staged"):
    """ stage food consumption and nutrient intake estimates data before loading to snowflake"""
    
    filenames = s3.list_files(src_bucket, dirname)
    result_df = pd.DataFrame()
    colnames = ["food/nutrient-group", "total-at-home", "total-afh", "restaurant", "fast-food", "school", "other", "demographic-group"]
    
    for file in filenames:
        df = s3.load_df(src_bucket, f"{dirname}/{file}", "csv")
        df['demographic-group'] = file.split(".")[0]
        df = df.drop('Unnamed: 0', axis=1)
        df.columns = colnames
        result_df = pd.concat([result_df, df], axis=0)
    
    return load_to_S3(s3, result_df, des_bucket, dirname)

    
def stage_foodexpenditure(s3: S3AWS, dirname: str, src_bucket: str = "s3-bucket-clean-usda", des_bucket: str = "s3-bucket-staged"):
    """ stage food expenditure series data before loading to snowflake"""
    
    filenames = s3.list_files(src_bucket, dirname)
    monthly_df = pd.DataFrame()
    nominal_df = pd.DataFrame()
    constant_df = pd.DataFrame()
    monthly_colnames = ["year", "month", "food_at_home", "food_away_from_home", "total_sales", "dollar_type"]
    
    for file in filenames:
        df = s3.load_df(src_bucket, f"{dirname}/{file}", "csv")
        df["dollar_type"] = file.split("-")[0]
        df = df.drop('Unnamed: 0', axis=1)
        
        if file == "constant-monthly-sale.csv" or file == "nominal-monthly-sale.csv":
            df.columns =  monthly_colnames
            monthly_df = pd.concat([monthly_df, df])
        else:
            if file.startswith("constant"):
                constant_df = pd.concat([constant_df, df], axis=1)         
            elif file.startswith("nominal"):
                nominal_df = pd.concat([nominal_df, df], axis=1)         
        
    expense_df = pd.concat([constant_df, nominal_df], axis=0)
    # drop duplicatec columns
    expense_df = expense_df.T.drop_duplicates().T 
    
    monthly_df["year"] = monthly_df["year"].map(lambda x: pd.to_datetime(f"{x}-01-01"))
    expense_df["year"] = expense_df["year"].map(lambda x: pd.to_datetime(f"{x}-01-01"))
    
    monthly = load_to_S3(s3, monthly_df, des_bucket,"monthly-sales-clean")
    expense = load_to_S3(s3, expense_df, des_bucket, dirname)
    return monthly & expense

def stage_priceindex(s3: S3AWS, dirname: str, src_bucket: str = "s3-bucket-clean-usda", des_bucket: str = "s3-bucket-staged"):
    """ stage price index data before loading to snowflake"""
    filenames = s3.list_files(src_bucket, dirname)
    result_df = pd.DataFrame()

    for file in filenames:
        df = s3.load_df(src_bucket, f"{dirname}/{file}", "csv")
        index_type = file.split("-")[0]
        df["price_index_type"] = index_type

        if index_type == "consumer":
            df = df.rename(columns = {"Consumer Price Index item": "price-index-item"})
        elif index_type == "producer":
            df = df.rename(columns = {"Producer Price Index item": "price-index-item"})
        result_df = pd.concat([result_df, df])        

    result_df = result_df.drop('Unnamed: 0', axis=1)
    return load_to_S3(s3, result_df, des_bucket, dirname)

    
def stage_foodavailability(s3: S3AWS, dirname: str, src_bucket: str = "s3-bucket-clean-usda", des_bucket: str = "s3-bucket-staged"):
    """ stage food availabilty data before loading to snowflake"""
    
    response =s3.client.list_objects_v2(Bucket=src_bucket, Prefix=dirname)
    files = response.get("Contents")
    paths = [file["Key"][file["Key"].find("/")+1:] for file in files]
    result_df = pd.DataFrame()
    
    for file in paths:
        df = s3.load_df(src_bucket, f"{dirname}/{file}", "csv")
        if file == "totals.csv" or file == "percents.csv":
            df = s3.load_df(src_bucket, f"{dirname}/{file}", "csv")
            key = file.split(".")[0]
            df = df.drop('Unnamed: 0', axis=1)
            idx = df.loc[df["Year"] == 2000].index[0] + 1
            df.loc[idx:idx, "Year"] = '2001'
            df["Year"] = df["Year"].map(lambda x: pd.to_datetime(f"{x}-01-01"))
            load_to_S3(s3, df, des_bucket, f"{key}-clean")
        else:
            df["type"] = file.split("/")[0]
            df["item name"] = file.split("/")[1].split(".")[0]
            if file in ["dairy/romano-cheese.csv", "dairy/ricotta-cheese.csv", "dairy/parmesan-cheese.csv", "dairy/provolone-cheese.csv"]:
                end = df.loc[df["year"] == 1994].index[0] +1 
                df = df.iloc[:end]
                df.dropna(inplace=True)
            result_df = pd.concat([result_df, df])
            
    result_df = result_df.drop('Unnamed: 0', axis=1)
    result_df = result_df.dropna(how="any")
    result_df["year"] = result_df["year"].map(lambda x: pd.to_datetime(f"{x}-01-01"))
    return load_to_S3(s3, result_df, des_bucket, f"{dirname}-clean")

def get_state_code(state: str):
    """ return iso US state code"""
    return US_STATE_CODE[state]

def stage_obesity_kaggle(s3: S3AWS, dirname: str, src_bucket: str = "s3-bucket-raw-kaggle", des_bucket: str = "s3-bucket-staged"):
    """ stage obesity data before loading to snowflake"""
    filenames = s3.list_files(src_bucket, dirname)
    
    for file in filenames:
        if file == "Obesity_GDP_PanelData.csv" or file == "obesity-cleaned.csv":
            df = s3.load_df(src_bucket, f"{dirname}/{file}", "csv")
            if "Unnamed: 0" in list(df.columns):
                df = df.drop('Unnamed: 0', axis=1)
                df["Obesity (%)"] = df["Obesity (%)"].apply(lambda x: x.split(" ")[0])
                df["Obesity (%)"] = df["Obesity (%)"].replace("No", np.nan)
            else:
                df["State_code"] = df['State'].apply(lambda x: get_state_code(x))
                df = df.drop(columns=["Adult.Obesity", "Poverty.Rate", "Real.GDP.Growth", "Region.Encoding", "Unit", "YearFE"])

            key = file.split(".")[0]
            df["Year"] = df["Year"].map(lambda x: pd.to_datetime(f"{x}-01-01"))
            load_to_S3(s3, df, des_bucket, f"{key}-clean")

    return True

def create_s3_bucket_stage(bucket_name):
    """ create s3 bucket for staging layer """
    s3 = S3AWS(ACCESS_KEY_ID, SECRET_ACCESS_KEY)
    return s3.create_bucket(bucket_name)

# key is directory name, value is staging function            
STAGING_LIST = {"obesity":stage_obesity_kaggle, 
                "fast-food-clean":stage_fastfood, 
                "food-consumption-estimates-clean":stage_foodnutrient_estimates,
                "nutrient-intake-estimates-clean":stage_foodnutrient_estimates,
                "food-expenditure-clean":stage_foodexpenditure,
                "price-index-clean":stage_priceindex,
                "loss-adjusted-food-availability-clean":stage_foodavailability
                }

def run(category):
    """ Run stager based on category"""
    
    # S3 instance
    s3 = S3AWS(ACCESS_KEY_ID, SECRET_ACCESS_KEY)
    # des_bucket = "s3-bucket-staged"
    # bucket = s3.create_bucket(des_bucket)
    staging_fn = STAGING_LIST[category]
    staging_fn(s3, category)

