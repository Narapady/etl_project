import sys
sys.path.append("..")

import os
from ingest.s3 import S3AWS

class FoodExpenditure:
    new_dir = "food-expenditure-clean"
    des_bucket = "s3-bucket-clean-usda" 
    src_bucket = "s3-bucket-raw-usda" 
    
    def __init__(self, dirname: str, s3: S3AWS):
        self.dirname = dirname 
        self.s3 = s3
    
    def process_food_expenditure(self) -> None:
        paths = [os.path.join(self.dirname, "constant_dollar_expenditures.xlsx"),
                 os.path.join(self.dirname, "nominal_expenditures.xlsx")]
        
        for path in paths:
            df = self.s3.load_df(self.src_bucket, path, "xlsx") 
            df.columns = df.iloc[3]
            df = df[4:29]
            year = df["Year"].tolist()
            result_dict = {col: i for i, col in enumerate(list(df.columns)) if "Total" in col} 
            df = df.drop("Year", axis=1)

            # breakpoint()
            start_pos = 0

            for k, end_pos in result_dict.items():
                new_df = df.iloc[:, start_pos:end_pos]
                new_df.insert(0, "year", year)
                
                new_df.reset_index(drop=True, inplace=True)
                prefix = path.split("/")[1].split("_")[0]
                filename = prefix + "-" + k.lower().replace(" ", "-") + ".csv"
                key = os.path.join(self.new_dir, filename)
                load_to_s3 = self.s3.df_to_s3(new_df, self.des_bucket, key) 
                if load_to_s3:
                    print(f"Successfully process {key} to S3")
                start_pos = end_pos + 1
                
    def process_monthly_sale(self) -> None:
        path = os.path.join(self.dirname, "monthly_sales.xlsx")
        df = self.s3.load_df(self.src_bucket, path, "xlsx")
        
        df.columns = ["year", "month", "nominal_fah", "nominal_fafh", "total_nominal_sales","constant_fah", "constant_fafh", "total_constant_sales"]
        df = df[3:307]
        nominal_df = df.drop(["constant_fah", "constant_fafh", "total_constant_sales"], axis=1)
        constant_df = df.drop(["nominal_fah", "nominal_fafh", "total_nominal_sales"], axis=1)
        
        nominal_df.reset_index(drop=True, inplace=True)
        constant_df.reset_index(drop=True, inplace=True)
        
        norminal_key = os.path.join(self.new_dir, "nominal-monthly-sale.csv")
        constant_key = os.path.join(self.new_dir, "constant-monthly-sale.csv")
        
        load_to_s3 = self.s3.df_to_s3(nominal_df, self.des_bucket, norminal_key) 
        if load_to_s3:
            print(f"Successfully process {norminal_key} to S3")
            
        load_to_s3 = self.s3.df_to_s3(constant_df, self.des_bucket,constant_key ) 
        if load_to_s3:
            print(f"Successfully process {constant_key} to S3")
        
# rm -rf food-expenditure-clean fast-food-clean price-index-clean nutrient-intake-estimates-clean loss-adjusted-food-availability-clean food-consumption-estimates-clean

