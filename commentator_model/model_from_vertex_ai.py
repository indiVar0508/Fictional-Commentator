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
def get_match_score(match_id):
    return RapidAPIFetcher.get_match_details(match_id)
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


# https://github.com/googleapis/python-aiplatform/blob/main/vertexai/generative_models/_generative_models.py#L1224
model = GenerativeModel(
    # Bit aggressive model!
    "gemini-1.0-pro",
    generation_config=GenerationConfig(temperature=0.8),
)

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

match_score_tool = Tool(function_declarations=[get_match_score_func])


def get_score_summary(match_id, commentator, show_name):
    prompt = f"""What is the score of match ID '{match_id}'"""

    response = model.generate_content(prompt, tools=[match_score_tool])
    score_response = get_match_score(
        **response.candidates[0].content.parts[0].function_call.args
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


# print(get_score_summary(90162, "Micheal Scott", "The Office"))
