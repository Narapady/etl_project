from storage.s3 import S3AWS
import os
import sys

sys.path.append("..")


class FastFood:
    """Tranform fast food data"""

    new_dir = "fast-food-clean"
    des_bucket = "s3-bucket-clean-usda"
    src_bucket = "s3-bucket-raw-usda"

    def __init__(self, dirname: str, s3: S3AWS):
        self.dirname = dirname
        self.s3 = s3

    def get_path(self) -> str:
        """get file path to s3 bucket"""
        if self.dirname == "2014":
            return os.path.join(self.dirname, f"table4_{self.dirname}.xls")

        return os.path.join(self.dirname, f"Table4_{self.dirname}.xlsx")

    def process_data(self) -> None:
        """clean, transform, and process data"""

        path = self.get_path()
        type = "xls" if self.dirname == 2014 else "xlsx"
        df = self.s3.load_df(self.src_bucket, path, type)

        if self.dirname == "2016":
            df.columns = [
                "times/week",
                "unit",
                "total",
                "men",
                "women",
                "total_se",
                "men_se",
                "women_se",
            ]
            end = df[df["times/week"] == "By age"].index[0] - 1
            df = df.iloc[3:end, :5]
        else:
            df.columns = ["times/week", "unit", "total", "men", "women"]
            end = df[df["times/week"] == "By age"].index[0] - 1
            df = df.iloc[3:end, :]

        df = df.dropna()
        age_group = ["age-15-and-older", "age-18-and-older"]
        middle = int(df.shape[0] / 2) + 1
        df1, df2 = df.iloc[:middle, :], df.iloc[middle:, :]

        df1.reset_index(drop=True, inplace=True)
        key1 = os.path.join(self.new_dir, f"{age_group[0]}-{self.dirname}.csv")
        load_to_s3 = self.s3.df_to_s3(df1, self.des_bucket, key1)
        if load_to_s3:
            print(f"Successfully process {key1} to S3")

        df2.reset_index(drop=True, inplace=True)
        key2 = os.path.join(self.new_dir, f"{age_group[1]}-{self.dirname}.csv")
        load_to_s3 = self.s3.df_to_s3(df2, self.des_bucket, key2)
        if load_to_s3:
            print(f"Successfully process {key2} to S3")
