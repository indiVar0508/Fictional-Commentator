import os
import random
import tweepy
import toml
import vertexai
from google.oauth2 import service_account

if os.path.exists(".streamlit/secrets.toml"):
    # locally
    with open(".streamlit/secrets.toml", "r") as f:
        config = toml.loads(f.read())
else:
    # gh-action
    config = toml.loads(os.environ["NEWS_SECRET"])


# intialize LLM model
credentials = service_account.Credentials.from_service_account_info(config["VERTEX_AI"])

scoped_credentials = credentials.with_scopes(
    ["https://www.googleapis.com/auth/cloud-platform"]
)

vertexai.init(
    project=config["VERTEX_AI"]["project_id"],
    location=config["VERTEX_AI"]["location"],
    credentials=scoped_credentials,
)

from commentator_model.model_from_vertex_ai import get_some_cricket_news  # noqa

# Intializd x Bot
bearer_token = config["X_BOT"]["bearer_token"]
api_key = config["X_BOT"]["api_key"]
api_secret_key = config["X_BOT"]["api_secret_key"]
consumner_key = config["X_BOT"]["consumner_key"]
consumer_secret_key = config["X_BOT"]["consumer_secret_key"]
access_token = config["X_BOT"]["access_token"]
access_secret_token = config["X_BOT"]["access_secret_token"]
client = tweepy.Client(
    bearer_token, api_key, api_secret_key, access_token, access_secret_token
)

commentator_details = [
    {
        "commentator": "Micheal Scott",
        "show_name": "The Office",
    },
    {
        "commentator": "Chandler Bing",
        "show_name": "Friends",
    },
    {
        "commentator": "Barney Stinson",
        "show_name": "How I met your mother",
    },
    {
        "commentator": "Rick Sanchez",
        "show_name": "Rick and Morty",
    },
    {
        "commentator": "Jake Paralata",
        "show_name": "Broklynn 99",
    },
    {
        "commentator": "Phil Dunphy",
        "show_name": "The Modern Family",
    },
]

character_detail = random.choice(commentator_details)
response = get_some_cricket_news(**character_detail, **config["FETCH_SCORE"])
tweet = f"Character picked {character_detail['commentator']} from show {character_detail['show_name']}:\n{response}\n#cricket #ai #genai #aiproject #100daysofmlcode"
tweet_thread = [tweet[i : i + 270] for i in range(0, len(tweet), 270)]
in_reply_to_tweet_id = None
for tweet in tweet_thread:
    response = client.create_tweet(
        text=tweet, in_reply_to_tweet_id=in_reply_to_tweet_id
    )
    in_reply_to_tweet_id = response.data["id"]
