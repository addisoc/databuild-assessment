import re
import sys
from configparser import ConfigParser

import duckdb
import pandas as pd

config = ConfigParser()
if len(sys.argv) < 2:
    print("Using default settings for normalization config.ini")
    config.read('config.ini')
else:
    print(f"Using custom configurations for normalization {sys.argv[1]}")
    config.read(sys.argv[1])

raw_ingredients = config['data.name']['raw.ingredients.list']
raw_path = config['data.location']['raw']
transformed_path = config['data.location']['transformed.ingredients']
normalized_parquet = config['data.name']['transformed.ingredients.normalized']
raw_folder = config['data.location']['raw']
raw_recipes = config['data.name']['raw.recipes.file']
transformed_ingredients = config['data.location']['transformed.ingredients']
ingredients_name = config['data.name']['raw.ingredients.list']

print("Normalizing ingredients")
# All ingredients
reference_list = pd.read_json(f'{raw_folder}/{ingredients_name}').term.to_list()

# would like to use duckdb for loading data but running into this issue: https://github.com/duckdb/duckdb/issues/6569
# Recipes
df = pd.read_json(f'{raw_folder}/{raw_recipes}')[['id', 'ingredients']]

# explode the data
db = duckdb.sql(
    "SELECT id, ingredients AS ingredient FROM (  SELECT id, UNNEST(ingredients) AS ingredients  FROM df) AS unnested")

# normalize the data: regex using all the ingredients piped together and then uses DuckDb's extract() to pull out the
# matches. There's no special logic so it will match Freshly Ground Black Pepper into Black Pepper
words = r'\b(?:' + '|'.join(re.escape(word) for word in reference_list) + r')\b'
query = f'''

SELECT
    id,
    regexp_extract(ingredient, '{words}') as ingredient

FROM 'db'

'''
duckdb.query(query).write_parquet(f'{transformed_path}/{normalized_parquet}')
