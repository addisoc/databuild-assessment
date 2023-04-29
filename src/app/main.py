from configparser import ConfigParser
from dataclasses import dataclass

import duckdb
from fastapi import FastAPI

app = FastAPI()

config = ConfigParser()
config.read('config.ini')
transformed_path = config['data.location']['transformed.ingredients']
normalized_parquet = config['data.name']['transformed.ingredients.normalized']


@dataclass
class CoocurrenceIngredent:
    ingredient: str
    coocurrence: dict


@app.get("/v1/ingredients-cooccurrence/{ingredient}")
async def root(ingredient: str, page: int = 0, limit: int = 10):
    return CoocurrenceIngredent(ingredient, _query(ingredient=ingredient, page = page, limit = limit))


def _query(ingredient: str, page, limit):
    df = f"{transformed_path}/{normalized_parquet}"
    query = f'''

    WITH ids AS (
    SELECT
        DISTINCT(id)
    FROM "{df}"
    WHERE ingredient = '{ingredient}'
    )
    
    SELECT 
        ingredient, 
        count(*) AS counts
    
    FROM "{df}"
    INNER JOIN ids ON ids.id = "{df}".id
    GROUP BY 1
    HAVING ingredient != '' AND ingredient != '{ingredient}'
    ORDER by 2 desc
    LIMIT '{limit}' OFFSET '{page * limit}'
    '''
    return duckdb.query(query).to_df().to_dict(orient='records')
