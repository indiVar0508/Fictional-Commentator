import streamlit as st
import time

from fictional_commentator.rapid_api_fetcher import RapidAPIFetcher
from streamlit_image_select import image_select
from commentator_model.model_from_vertex_ai import get_score_summary

st.set_page_config(
    page_title="Fictional Commentator",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(ttl=60)
def get_live_matches():
    return RapidAPIFetcher.get_all_live_matches()
    # Dummy Data
    # return {
    #     "matches": {
    #         92217: {
    #             "gameStatus": "Netherlands need 71 runs in 50 balls",
    #             "score": 91,
    #             "wickets": 1,
    #             "overs": 11.4,
    #             "matchType": "International",
    #             "matchFormat": "T20",
    #             "battingTeamName": "NED",
    #             "bowlingTeamName": "IRE",
    #             "name": "Netherlands T20I Tri-Series, 2024",
    #         },
    #         95454: {
    #             "gameStatus": "Gibraltar won by 5 wkts",
    #             "score": 175,
    #             "wickets": 5,
    #             "overs": 19.6,
    #             "matchType": "International",
    #             "matchFormat": "T20",
    #             "battingTeamName": "GIB",
    #             "bowlingTeamName": "BGR",
    #             "name": "Continental Cup 2024",
    #         },
    #         85405: {
    #             "gameStatus": "Day 1: 1st Session",
    #             "score": 87,
    #             "wickets": 3,
    #             "overs": 19.6,
    #             "matchType": "Domestic",
    #             "matchFormat": "TEST",
    #             "battingTeamName": "DERBY",
    #             "bowlingTeamName": "GLOUCS",
    #             "name": "County Championship Division Two 2024",
    #         },
    #         84317: {
    #             "gameStatus": "Day 1: 1st Session",
    #             "score": 54,
    #             "wickets": 4,
    #             "overs": 18.6,
    #             "matchType": "Domestic",
    #             "matchFormat": "TEST",
    #             "battingTeamName": "SOM",
    #             "bowlingTeamName": "DUR",
    #             "name": "County Championship Division One 2024",
    #         },
    #     }
    # }


# Persist ongoing matches
if "live_on_going_matches" not in st.session_state:
    st.session_state["live_on_going_matches"] = get_live_matches()


### Show Live Matches on the side bar as a drop down
# Fetch all Match details
data = st.session_state["live_on_going_matches"]
# Create a mapping b/w match name and match ID to get match details later!
match_name_to_id_mapping = {
    f'{match_detail["battingTeamName"]} vs {match_detail["bowlingTeamName"]}': match_id
    for match_id, match_detail in data["matches"].items()
}
with st.sidebar:
    live_match = st.sidebar.selectbox(
        "Select match you want your favorite character to commentate on!",
        match_name_to_id_mapping.keys(),
        index=None,
    )
### Show commentators on the side bar
# Commentators we support
# FIXME: Better allign images
# Jethalal - TMKUC - seems gemini model is not keeping essence of jetha :(
IMG_JETHIA = "./resources/jethalal.jpg"
# Micheal Scott - The Office
IMG_MICHEAL = "./resources/micheal.jpeg"
# Chandler - Friends
IMG_CHANDLER = "./resources/chandler.jpeg"
# Barney Stinson - HIMYM
IMG_BARNEY = "./resources/barney.jpeg"
# Rick - Rick and Morty
IMG_RICK = "./resources/rick.jpeg"
# Jake paralta - B99
IMG_JAKE = "./resources/jake.jpeg"
# Phil Dunphy - Modern Family
IMG_PHIL = "./resources/phil.jpg"

commentator_details = {
    IMG_JETHIA: {
        "commentator": "Jetha Lal",
        "show_name": "Tarak Mehta ka Ulta Chashma",
    },
    IMG_MICHEAL: {
        "commentator": "Micheal Scott",
        "show_name": "The Office",
    },
    IMG_CHANDLER: {
        "commentator": "Chandler Bing",
        "show_name": "Friends",
    },
    IMG_BARNEY: {
        "commentator": "Barney Stinson",
        "show_name": "How I met your mother",
    },
    IMG_RICK: {
        "commentator": "Rick Sanchez",
        "show_name": "Rick and Morty",
    },
    IMG_JAKE: {
        "commentator": "Jake Paralata",
        "show_name": "Broklynn 99",
    },
    IMG_PHIL: {
        "commentator": "Phil Dunphy",
        "show_name": "The Modern Family",
    },
}
with st.sidebar:
    st.markdown("### Select your favorite Commentator")
    COMMENTATOR = image_select(
        label="",
        images=[
            # Expected realistic output seen in GPT3.5 not getting same in gemini so disable for now
            # IMG_JETHIA,
            IMG_MICHEAL,
            IMG_CHANDLER,
            IMG_BARNEY,
            IMG_RICK,
            IMG_JAKE,
            IMG_PHIL,
        ],
        captions=[
            # "Jetha Lal",
            "Micheal Scott",
            "Chandler Bing",
            "Barney Stinson",
            "Rick Sanchez",
            "Jake Paralta",
            "Phil Dunphy",
        ],
        # index=None, is buggy
        use_container_width=False,
    )


st.session_state["say_welcome"] = True
# If no live match is happening
# FIXME: Make this pretty
if live_match is None:
    # Reset messages
    if "messages" in st.session_state:
        st.session_state.messages = []
    COMMENTATOR = None
# below logic can be better handled in on_change in selectboxh
elif (
    "selected_live_match" not in st.session_state
    or st.session_state["selected_live_match"] != live_match
):
    # Reset messages
    if "messages" in st.session_state:
        st.session_state.messages = []
    st.session_state["selected_live_match"] = live_match
    # check if commentator changed
    if (
        "current_commentator" not in st.session_state
        or st.session_state["current_commentator"] != COMMENTATOR
    ):
        st.session_state["current_commentator"] = COMMENTATOR
else:
    st.session_state["say_welcome"] = False


### Chat Bot related code
# Streamed response emulator
def welcome_message(commentator):
    if commentator is None:
        if len(match_name_to_id_mapping) == 0:
            response = "Welcome to Fictional Commentator, it seems currently there is no live match happening!"
        else:
            response = "Welcome to Fictional Commentator, Select match you want a summary on and a commentator from sidebar..."
    elif commentator == IMG_JETHIA:
        response = "Chaliye shuru kartey h!"
    elif commentator == IMG_MICHEAL:
        response = "You want me to do all the work, 'That's what she said!!'"
    elif commentator == IMG_BARNEY:
        response = "Hello there, lets make you awesome, Suit up!"
    elif commentator == IMG_CHANDLER:
        # FIXME: make this better later?!
        response = "So you need summary of match, could this be more obvious to watch a live match rather?"
    elif commentator == IMG_JAKE:
        response = "Cool.! cool! cool! cool! co..co. co.. co. cool! cool! col! co.co.co.... cool cool cool ! ! "
    elif commentator == IMG_PHIL:
        response = "I see you chose master himself"
    elif commentator == IMG_RICK:
        response = "In my dimension this sport is called gilly-danda, lets do it wubba lubba dub dub babyyy!!!!"
    return send_response_in_delay(response)


def send_response_in_delay(response):
    for word in response.split():
        yield word + " "
        time.sleep(0.08)


with st.expander("⚠ Disclaimer"):
    st.write(
        """
        This is a fun small project for purpose of learning function calling, the outputs can be factually incorrect
        This might still be buggy feel free to raise issue/improvments in issue tracker of the repository!
        """
    )
st.title("Score Summary Board")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
elif len(st.session_state["messages"]) > 2:
    st.session_state["messages"] = st.session_state["messages"][-1:]
# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=message["avatar"]):
        st.markdown(message["content"])


# Display assistant response in chat message container
with st.chat_message("assistant", avatar=COMMENTATOR):
    if st.session_state["say_welcome"]:
        response = st.write_stream(welcome_message(COMMENTATOR))
        if COMMENTATOR is not None:
            # FIXME: have to click fetch score twice issue!?
            st.session_state["say_welcome"] = False
    else:
        # get API response
        summary = get_score_summary(
            match_name_to_id_mapping[live_match], **commentator_details[COMMENTATOR]
        )
        response = st.write_stream(send_response_in_delay(summary))
# Add assistant response to chat history
st.session_state.messages.append(
    {"role": "assistant", "content": response, "avatar": COMMENTATOR}
)


def clear_session_message():
    st.session_state.messages = []


# Accept user input
st.button("Fetch Score", disabled=st.session_state["say_welcome"])
st.button(
    "Clear",
    disabled=len(st.session_state.messages) == 0,
    on_click=clear_session_message,
)
