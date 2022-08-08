from transform.food_availability import FoodAvailablity
from transform.nutrient_food_estimates import NutrientFoodEstimate
from transform.fast_food import FastFood
from transform.price_index import PriceIndex
from transform.food_expenditure import FoodExpenditure
from credential import ACCESS_KEY_ID, SECRET_ACCESS_KEY

from storage.s3 import S3AWS
from dotenv import load_dotenv

def run() -> None:

    # S3 instance
    s3 = S3AWS(ACCESS_KEY_ID, SECRET_ACCESS_KEY)
    bucket = s3.create_bucket("s3-bucket-clean-usda")
    
    if bucket:
        # Process food expenditure 
        food_exp = FoodExpenditure("current-food-expenditure-series", s3)
        food_exp.process_food_expenditure()
        food_exp.process_monthly_sale()

        # # Process consumer price index and producer price index
        # cpi = PriceIndex("consumer-price-index", "consumer", s3)
        # ppi = PriceIndex("producer-price-index", "producer", s3)
        # cpi.process_data()
        # ppi.process_data()

        # Process Food Availability 
        # food = FoodAvailablity("loss-adjusted-food-availability", s3)
        # food.process_data()

        # #Process nutrient intake and food consumption estimates
        # nutrient_estimate = NutrientFoodEstimate("nutrient-intake-estimates", s3)
        # food_estimate = NutrientFoodEstimate("food-consumption-estimates", s3)
        # nutrient_estimate.process_data()
        # food_estimate.process_data()
        #
        #  # Process fast food purchasers
        # dir_names = ["2014", "2015", "2016"]
        # for directiory in dir_names:
        #     fastfood = FastFood(directiory, s3)storage   fastfood.process_data()

