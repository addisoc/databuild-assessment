# All Recipes POC

Usage guide:

First install requirements
```
pip3 install -r requirements.txt
```

Then let's run the mini data pipeline by first downloading the raw file
`python3 transformations/download_raw_data.py`

Then we normalize the ingredients:
`python3 transformations/normalize_ingredients_data.py`


To run the service:
```
./run.sh
```

By default this will spin up the fast API on `localhost:8080`
Swagger can be found here: `http://localhost:8080/docs`
Configuration of the host and port can be done on the `run.sh` script.

The `GET` request to `localhost:8080/v1/ingredients-cooccurrence/{ingredient}`
will return the most frequently cooccurring ingredients. By default this will return 
the top ten results. However, you can set the pagination with `page` and `limit`:
`http://localhost:8080/v1/ingredients-cooccurrence/salt?page=0&limit=5`

```
{
  "ingredient": "salt",
  "coocurrence": [
    {
      "ingredient": "butter",
      "counts": 10156
    },
    {
      "ingredient": "all-purpose flour",
      "counts": 9966
    },
    {
      "ingredient": "white sugar",
      "counts": 9559
    },
    {
      "ingredient": "onion",
      "counts": 8300
    },
    {
      "ingredient": "black pepper",
      "counts": 7148
    }
  ]
}
```

## Assumptions
There were a few assumptions made that drove the architecture design.
1. There does not need to be real time insights. Data can be read on a schedule and does not need to be updated in real time.
2. Prioritize reads over writes. It seems logical that a recipe site would have more reads than writes so let's optimize for that

## Architecture and Design

![img_1.png](img_1.png)

Because we want to optimize for reads, I figured it would make sense to transform the data along the way and store it to disc.
In this situation it's optimized only for ingredient searching.
1. Raw data is first downloaded into the `data/raw` folder. The script to execute this can be found in `transformations/download_raw_data.py`. 
   * In this case we are downloaded the entire json of recipes and ingredients
   * in the future perhaps it would better to only download the new recipes that come in, perhaps on a nightly basis.
2. The data is then normalized to optimize for `ingredients` searching. The script to execute this can be found in `transformations/normalize_ingredients_data.py`
   * This scripts first explodes the data into individual rows 
   * Then does a regex to match approximately the `term` with the `ingredient` found in the github repo.
      * The regex is not the most accurate but I chose it for speed but since it can be also done separately from the query lookup this can be greatly improved.
3. The API then queries the saved parquet file for the most commonly used ingredients
   * Parquet was chosen mostly for read speeds. I tried also writing it as CSV which was quite a bit faster but in the end parquet seems faster to read so I went with that.

## Follow Up Items
* If I had more time I would have liked to have added more tests. I have a very simple test that checks the transformations but I should add another one for the query to find the similar ingredients
* The structure of the entire project is also not to my liking, but as I have almost no python experience I'm not quite sure what the proper structure is, and searching online gave me quite a varied result so I wasn't sure of the proper way.
* Requirement #2. I did not have time to implement this but judging by the similarity rating I think I would use something like [the Levenshtein distance](https://blog.paperspace.com/implementing-levenshtein-distance-word-autocomplete-autocorrect/#:~:text=The%20Levenshtein%20distance%20is%20a,transform%20one%20word%20into%20another.)
* Improve the fuzzy search. The regex works for the most part but there are definitely some gaps in the regex. For example in the ingredients list there is both `Black Pepper` and `Freshly Ground Pepper`. However, in the recipes there are over 2000 that refer to `freshly ground black pepper`, of which the regex matches to `black pepper`. This may or may not be the right answer depending on the need but something potentially to modify. There's also additionally some ingredients that do not match with anything at all so it can be improved.




Overall I found this pretty challenging but I'm happy I have at least a working version but I'm not quite satisfied with the Python code organization. It was however quite fun 
and I learned a lot, but I'm looking forward to hearing more about how I can improve upon this project!