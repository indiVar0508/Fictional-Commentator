"""
Long term look for scrapping for now for MVP go with api
Fetcher that leverages RapidAPI to do API call, currently we use it for getting cricbuzz live scores
We need two types of data for first prototype
  1. All Matches
  2. Details of specific match
"""

import random
from .data_fetcher.base_fetcher import BaseFetcher


class RapidAPIFetcher(BaseFetcher):
    @classmethod
    def get_all_live_matches(cls, url, api_key, api_host) -> dict:
        # Need to fetch all Live ongoing match
        all_live_matches: dict = cls.get_json_data(
            url=f"{url}/matches/v1/live",
            headers={
                "X-RapidAPI-Key": api_key,
                "X-RapidAPI-Host": api_host,
            },
        )
        # Filter out relevant information
        # What all do we need
        # matchID, state, team1, team2, battingteamID, bowlingTeamID inferable!, matchType, matchFormat, match_status
        # structure that can be prepared
        matches = {"matches": {}}
        for series in all_live_matches["typeMatches"]:
            # match_type = series["matchType"]
            for match_details in series["seriesMatches"]:
                if "seriesAdWrapper" in match_details:
                    # FIXME: for now just assumed that there is only one match
                    match_info = match_details["seriesAdWrapper"]["matches"][0][
                        "matchInfo"
                    ]
                    if match_info["stateTitle"] != "In Progress":
                        # If game is not started it won't have score
                        continue
                    # match_score = match_details["seriesAdWrapper"]["matches"][0][
                    #     "matchScore"
                    # ]
                    # get the matchID
                    match_id = match_info["matchId"]
                    # Name for now use Series Name itself
                    # name = match_info["seriesName"]
                    # match_format = match_info["matchFormat"]
                    # Who is batting
                    current_batting_team_id = match_info["currBatTeamId"]
                    # What is name of batting team and bowling team?
                    if current_batting_team_id == match_info["team1"]["teamId"]:
                        current_batting_name = match_info["team1"]["teamSName"]
                        # batting_team_score_alias = "team1Score"
                        # _bowling_team_score_alias = "team2Score"
                        current_bowling_name = match_info["team2"]["teamSName"]
                    else:
                        current_batting_name = match_info["team2"]["teamSName"]
                        # batting_team_score_alias = "team2Score"
                        # _bowling_team_score_alias = "team1Score"
                        current_bowling_name = match_info["team1"]["teamSName"]
                    # What is batting score?
                    # FIXME: Assume only on inning
                    # batting_team_score = match_score[batting_team_score_alias][
                    #     "inngs1"
                    # ]["runs"]
                    # batting_wickets = match_score[batting_team_score_alias]["inngs1"][
                    #     "wickets"
                    # ]
                    # batting_overs = match_score[batting_team_score_alias]["inngs1"][
                    #     "overs"
                    # ]
                    # game_status = match_info["status"]
                    # FIXME: Long term focus should be to get more details and we should move away from API to web scraping
                    #        or some free developer api
                    matches["matches"][match_id] = {
                        "battingTeamName": current_batting_name,
                        "bowlingTeamName": current_bowling_name,
                    }
        return matches

    @classmethod
    def get_match_details(cls, url, api_key, api_host, match_id) -> dict:
        response: dict = cls.get_json_data(
            url=f"{url}/mcenter/v1/{match_id}/leanback",
            headers={
                "X-RapidAPI-Key": api_key,
                "X-RapidAPI-Host": api_host,
            },
        )
        match_details = {}
        match_details["batsman_name"] = response["miniscore"]["batsmanStriker"].get(
            "batName", "Failed to get name"
        )
        match_details["batsman_score"] = response["miniscore"]["batsmanStriker"].get(
            "batRuns", "Failed to get name"
        )
        match_details["batsman_bowled"] = response["miniscore"]["batsmanStriker"].get(
            "batBalls", "Failed to get name"
        )

        match_details["non_striker_batsman_name"] = response["miniscore"][
            "batsmanNonStriker"
        ].get("batName", "Failed to get name")
        match_details["non_striker_batsman_score"] = response["miniscore"][
            "batsmanNonStriker"
        ].get("batRuns", 0)
        match_details["non_striker_batsman_bowled"] = response["miniscore"][
            "batsmanNonStriker"
        ].get("batBalls", 0)

        match_details["score"] = response["miniscore"]["batTeam"].get("teamScore", 0)
        match_details["wickets"] = response["miniscore"]["batTeam"].get("teamWkts", 0)
        match_details["overs"] = response["miniscore"].get("overs", 0)
        match_details["current_runrate"] = response["miniscore"].get(
            "currentRunRate", 0
        )

        match_details["bowler_name"] = response["miniscore"]["bowlerStriker"].get(
            "bowlName", "Failed to get name"
        )
        match_details["bowler_economy"] = response["miniscore"]["bowlerStriker"].get(
            "bowlWkts", 0
        )
        match_details["bowler_wickets"] = response["miniscore"]["bowlerStriker"].get(
            "bowlWkts", -1
        )
        batting_team_id = response["miniscore"]["batTeam"].get("teamId", -1)
        if batting_team_id == response["matchHeader"]["team1"].get("id"):
            match_details["batting_team_name"] = response["matchHeader"]["team1"].get(
                "name", "Failed to get name"
            )
            match_details["bowling_team_name"] = response["matchHeader"]["team2"].get(
                "name", "Failed to get name"
            )
        else:
            match_details["batting_team_name"] = response["matchHeader"]["team2"].get(
                "name", "Failed to get name"
            )
            match_details["bowling_team_name"] = response["matchHeader"]["team1"].get(
                "name", "Failed to get name"
            )
        return match_details

    @classmethod
    def get_some_random_news(cls, url, api_key, api_host) -> str:
        """
        Route responsible to fetch current stats and analysis
        """
        response: dict = cls.get_json_data(
            url=f"{url}/news/v1/index",
            headers={
                "X-RapidAPI-Key": api_key,
                "X-RapidAPI-Host": api_host,
            },
        )
        # Remove ads & select a random story
        story = random.choice(
            list(filter(lambda x: "ad" not in x, response["storyList"]))
        )["story"]
        # get details of story!
        response: dict = cls.get_json_data(
            url=f"{url}/news/v1/detail/{story['id']}",
            headers={
                "X-RapidAPI-Key": api_key,
                "X-RapidAPI-Host": api_host,
            },
        )
        # remove ads
        content = list(filter(lambda x: "ad" not in x, response["content"]))
        # build up story
        news = "".join([c.get("content", {}).get("contentValue", "") for c in content])
        assert len(news) > 0, "Failed to parse news"
        return news
