import re
from configparser import ConfigParser

import duckdb
import pandas as pd
import sys


config = ConfigParser()
if sys.argv[1] is None:
    config.read('config.ini')
else:
    config.read(sys.argv[1])

raw_ingredients = config['data.name']['raw.ingredients.list']
raw_path = config['data.location']['raw']
transformed_path = config['data.location']['transformed.ingredients']
normalized_parquet = config['data.name']['transformed.ingredients.normalized']
raw_folder = config['data.location']['raw']
raw_recipes = config['data.name']['raw.recipes.file']
transformed_ingredients = config['data.location']['transformed.ingredients']
ingredients_name = config['data.name']['raw.ingredients.list']

# All ingredients
reference_list = pd.read_json(f'{raw_folder}/{ingredients_name}').term.to_list()

# would like to use duckdb for loading data but running into this issue: https://github.com/duckdb/duckdb/issues/6569
# Recipes
df = pd.read_json(f'{raw_folder}/{raw_recipes}')[['id', 'ingredients']]

# explode the data
db = duckdb.sql(
    "SELECT id, ingredients AS ingredient FROM (  SELECT id, UNNEST(ingredients) AS ingredients  FROM df) AS unnested")

# normalize the data
words = r'\b(?:' + '|'.join(re.escape(word) for word in reference_list) + r')\b'
query = f'''

SELECT
    id,
    regexp_extract(ingredient, '{words}') as ingredient

FROM 'db'

'''
duckdb.query(query).write_parquet(f'{transformed_path}/{normalized_parquet}')
