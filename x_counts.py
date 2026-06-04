import os
import requests

X_COUNTS_ENDPOINT = "https://api.x.com/2/tweets/counts/recent"

def get_x_post_count(title: str) -> int:
    token = os.getenv("X_BEARER_TOKEN")

    if not token:
        return 0

    query = f'"{title}" lang:ja -is:retweet'

    response = requests.get(
        X_COUNTS_ENDPOINT,
        headers={
            "Authorization": f"Bearer {token}"
        },
        params={
            "query": query,
            "granularity": "day"
        }
    )

    response.raise_for_status()

    data = response.json()

    return sum(
        item.get("tweet_count", 0)
        for item in data.get("data", [])
    )
