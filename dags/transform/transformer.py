from transform.food_availability import FoodAvailablity
from transform.nutrient_food_estimates import NutrientFoodEstimate
from transform.fast_food import FastFood
from transform.price_index import PriceIndex
from transform.food_expenditure import FoodExpenditure
from credential import ACCESS_KEY_ID, SECRET_ACCESS_KEY
from storage.s3 import S3AWS

# list of directory to store tranformed data
USDA_TRANSFORM_LIST = (
        "current-food-expenditure-series",
        "consumer-price-index",
        "producer-price-index",
        "nutrient-intake-estimates",
        "food-consumption-estimates",
        # "loss-adjusted-food-availability"
        "2014",
        "2015",
        "2016"
        )

def create_s3_bucket_transform(bucket_name):
    """ create s3 bucket for transformation layer """
    
    s3 = S3AWS(ACCESS_KEY_ID, SECRET_ACCESS_KEY)
    return s3.create_bucket(bucket_name)

def tranform_data(category, s3):
    """ tranform data based on category or directory name"""
    
    if category == "current-food-expenditure-series":
        food_exp = FoodExpenditure(category, s3)
        food_exp.process_food_expenditure()
        food_exp.process_monthly_sale()    
    elif category == "consumer-price-index":
        cpi = PriceIndex(category, "consumer", s3)
        cpi.process_data()
    elif category == "producer-price-index":
        ppi = PriceIndex(category, "producer", s3)
        ppi.process_data()
    elif category == "loss-adjusted-food-availability":
        food = FoodAvailablity(category, s3)
        food.process_data()
    elif category == "nutrient-intake-estimates" or category == "food-consumption-estimates":
        nutrient_food_estimate = NutrientFoodEstimate(category, s3)
        nutrient_food_estimate.process_data()
    elif category in ["2014", "2015", "2016"]:
            fastfood = FastFood(category, s3)
            fastfood.process_data()
    
def run(category): 
    """Run the transformer base on category"""
    # S3 instance
    s3 = S3AWS(ACCESS_KEY_ID, SECRET_ACCESS_KEY)
    tranform_data(category, s3)
