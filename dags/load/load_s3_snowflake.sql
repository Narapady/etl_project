-- Create database and data warehouse
create or replace database us_food_nutrition;
use database us_food_nutrition;
use schema us_food_nutrition.public;

create or replace warehouse food_nutrition_wh with
  warehouse_size='X-SMALL'
  auto_suspend = 180
  auto_resume = true
  initially_suspended=true;

use warehouse food_nutrition_wh;
select current_warehouse();

-- Integrate with Preset for visulization
create network policy PRESET_WHITELIST
ALLOWED_IP_LIST = ('44.193.153.196', '52.70.123.52', '54.83.88.93')

-- Create tables
create or replace table monthly_sales (
    id int,
    year datetime,
    month string,
    fah_sale float,
    fafh_sale float,
    total_sales float,
    dollar_type string
);

create or replace table food_availability_calories (
    id int,
    year datetime,
    protein float,
    dairy float,
    fruit float,
    veggie float,
    flour_and_cereal float,
    fat_oil_dairy_fat float,
    sugar_and_sweeteners float,
    total_calories float
);

create or replace table food_availability_percent (
    id int,
    year datetime,
    protein float,
    dairy float,
    fruit float,
    veggie float,
    flour_and_cereal float,
    fat_oil_dairy_fat float,
    sugar_and_sweeteners float,
    total_percentages float
);

create or replace table daily_food_availability(
    id int,
    year datetime,
    original_weight float,
    edible_weight float,
    total_percent_loss float,
    loss_lbs_per_year float,
    loss_gram_per_day float,
    available_calories_per_day float,
    type string,
    item_name string
);

create or replace table food_consumption_estimates(
    id int,
    food_nutrient_group string,
    total_at_home float,
    total_away_from_home float,
    restaurant float,
    fast_food float,
    school float,
    other float,
    demographic_year string
);

create or replace table nutrient_intake_estimates(
    id int,
    food_nutrient_group string,
    total_at_home float,
    total_away_from_home float,
    restaurant float,
    fast_food float,
    school float,
    other float,
    demographic_year string
);

create or replace table food_expenditure(
    id int,
    year datetime,
    hotels_motels_alcohol float,
    other_aafh float,
    total_aafh float,
    dollar_type string,
    food_stores float,
    other_aah float,
    total_aah float,
    restaurants float,
    drinking_places float,
    hotels_motels_food float,
    retail_stores_and_vending float,
    recreational_places float,
    schools float,
    other_fafh float,
    food_furnished_and_donated float,
    total_fafh float,
    grocery_stores float,
    convenience_stores float,
    other_foodstores float,
    clubs_and_supercenters float,
    other_stores_and_foodservicef float,
    mail_order_and_home_delivery float,
    farmers_manufacturers_wholesalers float,
    home_production_and_donation float,
    total_fah float
);

create or replace table fast_food(
    id int,
    times_per_week string,
    unit string,
    total float,
    men float,
    women float,
    year int,
    age_group string
);

create or replace table price_index(
    id int,
    price_index_item string,
    pc_1974 float,
    pc_1975 float,
    pc_1976 float,
    pc_1977 float,
    pc_1978 float,
    pc_1979 float,
    pc_1980 float,
    pc_1981 float,
    pc_1982 float,
    pc_1983 float,
    pc_1984 float,
    pc_1985 float,
    pc_1986 float,
    pc_1987 float,
    pc_1988 float,
    pc_1989 float,
    pc_1990 float,
    pc_1991 float,
    pc_1992 float,
    pc_1993 float,
    pc_1994 float,
    pc_1995 float,
    pc_1996 float,
    pc_1997 float,
    pc_1998 float,
    pc_1999 float,
    pc_2000 float,
    pc_2001 float,
    pc_2002 float,
    pc_2003 float,
    pc_2004 float,
    pc_2005 float,
    pc_2006 float,
    pc_2007 float,
    pc_2008 float,
    pc_2009 float,
    pc_2010 float,
    pc_2011 float,
    pc_2012 float,
    pc_2013 float,
    pc_2014 float,
    pc_2015 float,
    pc_2016 float,
    pc_2017 float,
    pc_2018 float,
    pc_2019 float,
    pc_2020 float,
    pc_2021 float,
    pc_2022 float,
    price_index_type string
);

create or replace table obesity_world(
    id int,
    country string,
    year datetime,
    obesity_percent float,
    sex string
);

create or replace table obesity_gdp(
    id int,
    state string,
    year datetime,
    obesity_rate float,
    average_age float,
    average_income float,
    population int,
    poverty_rate float,
    real_gdp float,
    real_gdp_growth float,
    real_personal_income float,
    region string,
    real_gdp_percapita float,
    state_code string
);

-- Load from S3 to snowflake
copy into monthly_sales
    from @s3_stage/monthly-sales-staged.csv
    on_error = 'skip_file';

copy into food_availability_calories
    from @s3_stage/totals-staged.csv
    on_error = 'skip_file';

copy into food_availability_percent
    from @s3_stage/percents-staged.csv
    on_error = 'skip_file';
    
copy into daily_food_availability
    from @s3_stage/loss-adjusted-food-availability-staged.csv
    on_error = 'skip_file';
    
copy into food_consumption_estimates
    from @s3_stage/food-consumption-estimates-staged.csv
    on_error = 'skip_file';
    
copy into nutrient_intake_estimates
    from @s3_stage/nutrient-intake-estimates-staged.csv
    on_error = 'skip_file';

copy into food_expenditure
    from @s3_stage/food-expenditure-staged.csv
    on_error = 'skip_file';

copy into fast_food
    from @s3_stage/fast-food-staged.csv
    on_error = 'skip_file';
    
copy into price_index
    from @s3_stage/price-index-staged.csv
    on_error = 'skip_file';
    
copy into obesity_world
    from @s3_stage/obesity-staged.csv
    on_error = 'skip_file';
    
copy into obesity_gdp
    from @s3_stage/Obesity_GDP_PanelData-staged.csv
    on_error = 'skip_file';
