import duckdb
import unittest
from os import system


# very simple test to check transformations
class TestNormalize(unittest.TestCase):
    def test(self):
        system("python3 ../../transformations/normalize_ingredients_data.py ../test-config.imi")
        parquet_file = '../data/transformed/ingredients/normalized_ingredients.parquet'
        self.assertEqual(193, duckdb.sql(f"SELECT * FROM '{parquet_file}'").df().shape[0])
        self.assertEqual(3, duckdb.sql(f"SELECT * FROM '{parquet_file}' WHERE id = 11125").df().shape[0])
