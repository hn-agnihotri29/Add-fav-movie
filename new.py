import requests

MOVIE_DB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
MOVIE_DB_API_KEY = "92f54424a3465deeb0b6b58fedfec19b"

query = {
    "api_key": MOVIE_DB_API_KEY,
}

movie_id = 372058
response = requests.get(f"{MOVIE_DB_SEARCH_URL}/{movie_id}", params=query)
print(response)
