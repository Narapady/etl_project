import numpy as np
import os
from storage.s3 import S3AWS


class PriceIndex:
    """Transform consumer and producer price index data"""

    new_dir = "price-index-clean"
    des_bucket = "s3-bucket-clean-usda"
    src_bucket = "s3-bucket-raw-usda"

    def __init__(self, dirname: str, pi_type: str, s3: S3AWS):
        self.dirname = dirname
        self.pi_type = pi_type
        self.s3 = s3

    def get_2022_pct_change(self, path: str):
        """return a list of percentage change in price index base on price index type"""
        df = self.s3.load_df(self.src_bucket, path, "xlsx")
        if self.pi_type == "consumer":
            col = "Forecast range2 2022"
        elif self.pi_type == "producer":
            col = "Forecast range1 2022"

        df.columns = df.iloc[0]
        df = df[2:].dropna(how="all")
        pct_change = df[col].tolist()[:-5]
        result = []
        for pct in pct_change:
            if pct is np.nan:
                result.append(np.nan)
            elif "to" in pct:
                num = pct.split("to")
                num1, num2 = float(num[0].strip()[:3]), float(
                    num[1].strip()[:3])
                result.append(np.mean([num1, num2]))

        return result

    def get_path(self):
        """construct file path"""
        if self.dirname == "consumer-price-index":
            filename = "historicalcpi.xlsx"
        elif self.dirname == "producer-price-index":
            filename = "historicalppi.xlsx"

        return os.path.join(self.dirname, filename)

    def process_data(self):
        """transformk, clean, and process price index data"""
        path = self.get_path()
        df = self.s3.load_df(self.src_bucket, path, "xlsx")
        df.columns = df.iloc[0]

        if self.pi_type == "consumer":
            df = df.iloc[1:27, : list(df.columns).index(
                2021.0) + 1].dropna(how="all")
            pct_change_2022_path = os.path.join(
                self.dirname, "CPIforecast.xlsx")

        elif self.pi_type == "producer":
            df = df.iloc[1:26, : list(df.columns).index(
                2021.0) + 1].dropna(how="all")
            pct_change_2022_path = os.path.join(
                self.dirname, "PPIforecast.xlsx")

        cols = [str(year) for year in list(df.columns)]
        cols[1:] = [year[:-2] for year in cols[1:]]
        df.columns = cols

        df.insert(df.shape[1], "2022",
                  self.get_2022_pct_change(pct_change_2022_path))
        df.reset_index(drop=True, inplace=True)

        key = os.path.join(self.new_dir, f"{self.pi_type}-price-index.csv")

        load_to_s3 = self.s3.df_to_s3(df, self.des_bucket, key)
        if load_to_s3:
            print(f"Successfully process {key} to S3")
