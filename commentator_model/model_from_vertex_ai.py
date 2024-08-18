# Import relevant thigns
from vertexai.generative_models import (
    Content,
    FunctionDeclaration,
    GenerativeModel,
    Part,
    Tool,
    GenerationConfig,
)
from cachetools import cached, TTLCache
from fictional_commentator.rapid_api_fetcher import RapidAPIFetcher


# Cache for 30s to avoid overspamming
@cached(cache=TTLCache(maxsize=5, ttl=30))
def get_match_score(url, api_key, api_host, match_id):
    return RapidAPIFetcher.get_match_details(url, api_key, api_host, match_id)
    # Dummy data
    # return {
    #     "batsman_name": "Dhruv Jurel",
    #     "batsman_score": 55,
    #     "batsman_bowled": 31,
    #     "non_striker_batsman_name": "Trent Boult",
    #     "non_striker_batsman_score": 0,
    #     "non_striker_batsman_bowled": 3,
    #     "score": 138,
    #     "wickets": 7,
    #     "overs": 19.2,
    #     "current_runrate": 7.14,
    #     "bowler_name": "T Natarajan",
    #     "bowler_economy": 5.1,
    #     "bowler_wickets": 1,
    #     "bating_team": "RR",
    #     "bowling_team": "SRH",
    # }


@cached(cache=TTLCache(maxsize=5, ttl=30))
def get_cricket_news(url: str, api_key: str, api_host: str) -> str:
    return RapidAPIFetcher.get_some_random_news(url, api_key, api_host)


# https://github.com/googleapis/python-aiplatform/blob/main/vertexai/generative_models/_generative_models.py#L1224
model = GenerativeModel(
    # Bit aggressive model!
    "gemini-1.0-pro",
    generation_config=GenerationConfig(temperature=0.8),
)

# Define tools
get_match_score_func = FunctionDeclaration(
    name="get_match_score",
    description="get scoreboard detail for a given match ID",
    parameters={
        "type": "object",
        "properties": {
            "match_id": {
                "type": "string",
                "description": "Match ID for which score will be fetched",
            }
        },
        "required": ["match_id"],
    },
)

# get_cricket_news_func = FunctionDeclaration(
#     name="get_cricket_news",
#     description="gets story or news of some latest related cricket or its players",
#     # TODO: make this more dynamica and specific like category, region etc.
#     parameters={},
# )


match_score_tool = Tool(function_declarations=[get_match_score_func])


def get_score_summary(match_id, commentator, show_name, url, api_key, api_host):
    prompt = f"""What is the score of match ID '{match_id}'"""

    response = model.generate_content(prompt, tools=[match_score_tool])
    score_response = get_match_score(
        url,
        api_key,
        api_host,
        **response.candidates[0].content.parts[0].function_call.args,
    )
    # Dummy data
    # return "some long string asfdmowidgfo reanglinas erinvlareifnpao sdmkave; feijngjvs dmvkpiaeroamf efovmosfp, jier9mjo9mjc fgrcneoricuromcf li a,x,eroim  cewr u oifnmeoifcnh 90o,uwgfkneslfciwerc src,oei"

    response = model.generate_content(
        [
            Content(
                role="user",
                parts=[
                    Part.from_text(
                        prompt
                        + f"Pretend that you are {commentator} from the show {show_name}, and try to commentate the score in the way {commentator} would have done, try to add zingy refrence from the show {show_name} while being factually correct under 150 words, do not mention the match id in your response"
                    ),
                ],
            ),
            Content(
                role="function",
                parts=[
                    Part.from_dict(
                        {
                            "function_call": {
                                "name": "get_match_score",
                            }
                        }
                    )
                ],
            ),
            Content(
                role="function",
                parts=[
                    Part.from_function_response(
                        name="get_match_score",
                        response={
                            "content": score_response,
                        },
                    )
                ],
            ),
        ],
        tools=[match_score_tool],
    )

    return response.candidates[0].content.parts[0].text


def get_some_cricket_news(commentator, show_name, url, api_key, api_host):
    news = get_cricket_news(url, api_key, api_host)

    prompt = f"""
    You are a social media manager managing a twitter account,
    You need to create a post summarizing summarising below mentioned article detail in less than 270 characters
    be precised and professional while pretending to be {commentator} from the show {show_name}.

    Your story is 
    `{news}`
    
    Try to add quirks and references from {show_name} while being polite and friendly summary, 
    NOTE: *you have a character limit of 270 characters*
    """

    response = model.generate_content(prompt)
    return response.candidates[0].content.parts[0].text
