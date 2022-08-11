import sys
sys.path.append("..")

import os
from storage.s3 import S3AWS

def get_dirname(input_str: str) -> str:
    " return new format directory name "
    
    s = input_str.split("/")[0]
    s = "".join(s)
    return s.lower().replace(" ", "-")

class NutrientFoodEstimate:
    """ Transform nutrition intake and food consumpiton estimates data"""
    
    des_bucket = "s3-bucket-clean-usda" 
    src_bucket = "s3-bucket-raw-usda" 
    
    def __init__(self, dirname: str, s3: S3AWS):
        self.dirname = dirname 
        self.new_dir = self.dirname.lower().replace(" ", "-") + "-clean"
        self.s3 = s3
        
    def change_name(self, input_str: str):
        """ change column names"""
        input_str = input_str.strip()
        if input_str == "Total population1":
            return "Total population"
        if input_str == "Adults age 20–642":
            return "Adults age 20-64"
        if input_str == "Seniors age 65 and above2":
            return "Seniors age 65 and above"
        return input_str

    def get_columns(self):
        """ get dataframe columns based on directory name """
        
        col_names = [
        "total-2015-2016",
        "at-home-2015-2016",
        "total_afh-2015-2016",
        "restaurant-2015-2016",
        "fast-food-2015-2016",
        "school-2015-2016",
        "other_afh-2015-2016",
        "total-2017-2018",
        "at-home-2017-2018",
        "total_afh-2017-2018",
        "restaurant-2017-2018",
        "fast-food-2017-2018",
        "school-2017-2018",
        "other_afh-2017-2018",
        ]
        
        if self.dirname.startswith("nutrient"):
            col_names.insert(0, 'nutrient-group')
        elif self.dirname.startswith("food"): 
            col_names.insert(0, 'food-group')
        
        return col_names

    def get_path(self) -> str:
        if self.dirname.startswith("nutrient"):
            filename = "nutrient_table1.xlsx"
        elif self.dirname.startswith("food"): 
            filename = "food_table1.xlsx"
            
        return os.path.join(self.dirname, filename)
        
    def process_data(self):
        "transform, clean and process data"    
        
        path = self.get_path()    
        df = self.s3.load_df(self.src_bucket, path, 'xlsx')
        
        df.columns = self.get_columns()
        first_col = list(df.columns)[0]
        end = 0

        for val in df[first_col].unique():
            if "Note" in str(val):
                end = df[df[first_col] == val].index[0]
        df = df[3:end]

        group = []
        for i, row in df.iterrows():
            if "(" in row[first_col]:
                group.append(row[first_col])
                df = df.drop(i)

        df[first_col] = df[first_col].apply(lambda x: self.change_name(x))
        demographics = df[first_col].unique()      

        for demo in demographics:
            new_df = df[df[first_col] == demo]
            new_df = new_df.drop(columns=first_col)
            df1, df2 = new_df.iloc[:, 1:7], new_df.iloc[:, 8:]
            df1.insert(0, first_col, group)
            df2.insert(0, first_col, group)
            
            df1.reset_index(drop=True, inplace=True)
            df1_postfix = list(df1.columns)[1][8:]
            key1 = os.path.join(self.new_dir, f"{demo}-{df1_postfix}.csv")
            load_to_s3 = self.s3.df_to_s3(df1, self.des_bucket, key1) 
            if load_to_s3:
                print(f"Successfully process {key1} to S3")
            
            df2.reset_index(drop=True, inplace=True)
            df2_postfix = list(df2.columns)[1][8:]
            key2 = os.path.join(self.new_dir, f"{demo}-{df2_postfix}.csv")
            load_to_s3 = self.s3.df_to_s3(df2, self.des_bucket, key2) 
            if load_to_s3:
                print(f"Successfully process {key2} to S3")
           
