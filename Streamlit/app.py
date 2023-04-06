import streamlit as st
import pandas as pd
import template as t
# import authenticate as a
import json
from itertools import cycle
from random import random
import liveCalc as LC
import searchResults as SR
import colabborative_reccomendations as CR
import numpy as np

TRAINING = True

search_bar_placeholder_text = "Zoeken..."

st.set_page_config(layout="wide")
# # Depreciated
# df_NPO = pd.read_csv("data/NPOPlayer.csv", sep=";")
# df_NPO = pd.read_csv("data/NPO_mike.csv")

df_NPO = pd.read_csv("data/NPOPlayerv2.csv")

# open the activities json file
with open('data/activities.json') as json_file:
    users_activities = json.load(json_file)

# some small data cleaning that slould be partially moved to pre processing if time allows it...
df_NPO["thumbnail"].fillna("no-image.png", inplace=True)
df_NPO["longSummary"].fillna("", inplace=True)
df_NPO['mainTitle'].fillna('', inplace=True)

# create a session state
if 'user' not in st.session_state:
    st.session_state['user'] = LC.generate_random_userID(10)

if 'activities' not in st.session_state:
    st.session_state['activities'] = users_activities

if 'mediaID' not in st.session_state:
    st.session_state['mediaID'] = 'WO_POWN_8513746'

if 'user_search_query' not in st.session_state:
    st.session_state['user_search_query'] = search_bar_placeholder_text

if 'df_NPO' not in st.session_state:
    st.session_state['df_NPO'] = df_NPO

if 'mainTitle' not in st.session_state:
    st.session_state['mainTitle'] = df_NPO[df_NPO['mediaID'] == st.session_state['mediaID']]["mainTitle"].values[0]

if 'season' not in st.session_state:
    st.session_state['season'] = df_NPO[df_NPO['mediaID'] == st.session_state['mediaID']]["season"].values[0]

if 'userRecommendations' not in st.session_state:
    st.session_state['userRecommendations'] = None  # We need a placeholder


# Retrieve mediaID from session state.
# Since we use these quite a lot, easier to retrieve now, than to keep querying
df_selected_mediaID = df_NPO[df_NPO['mediaID'] == st.session_state['mediaID']]
df_selected_mainTitle = df_NPO[df_NPO['mainTitle'] == st.session_state['mainTitle']]
available_seasons = list(df_selected_mainTitle['season'].sort_values().unique())

################################################
# Shown on page:
################################################

# ONLY USED FOR TRAINING THE PERSONAL RECOMMENDATION
# Show a text input where the user can manually override the userID
if TRAINING:
    userID = st.text_input('UserID', st.session_state['user'])
    if userID != st.session_state['user']:
        st.session_state['user'] = userID
    st.session_state['userRecommendations']

st.button("Calculate new personal recommendations", key=random(), on_click=CR.renewPersonalRecomedations, args=(st.session_state['user'], df_NPO))

user_search_query = st.text_input('Movie title', search_bar_placeholder_text, label_visibility="collapsed")

# If the user made a search, show the results
if(user_search_query != search_bar_placeholder_text and user_search_query != ""):
    st.session_state['user_search_query'] = user_search_query
    with st.expander("search", expanded=True):
        t.tiles(SR.get_search_result_v2(df_NPO ,user_search_query, 5))

# Visuelisation of the current selected mediaID
col1, col2 = st.columns(2)
with col1:
    st.image(str(df_selected_mediaID['thumbnail'].values[0]), use_column_width='always',output_format="JPEG")

with col2:
    st.title(df_selected_mediaID['mainTitle'].values[0])
    st.caption(df_selected_mediaID['broadcaster'].values[0])
    st.caption(str(df_selected_mediaID['subTitle'].values[0]))
    st.markdown(df_selected_mediaID['longSummary'].values[0])
    season = st.selectbox('Kies seizoen:', available_seasons, index=available_seasons.index(df_selected_mediaID['season'].values[0]))
    st.radio("Beoorderling", options=(['no rating', '1', '2','3', '4', '5']), key="rating", horizontal =True, on_change=t.activity, args=(df_selected_mediaID['mediaID'].values[0], '1'))


with st.expander("(Persoonlijke) aanbevelingen", expanded=True):
    t.tiles(LC.getRecommendations(df_NPO, st.session_state['mediaID'], 10))


with st.expander("Meer van dit seizoen"):
    available_episodes = df_selected_mainTitle.loc[(df_selected_mainTitle['season'] == season)]
    rows = int(available_episodes.shape[0] / 10) +1 # small calculation on how many episodes to show per row
    for i in range(rows):
        minrow = i*10
        maxrow = min(minrow + 10, available_episodes.shape[0])
        t.tiles(available_episodes.iloc[minrow:maxrow])


# # Depreciated
# with st.expander('Implicit and Explicit feedback'):
#     st.button('👍', key=random(), on_click=t.activity, args=(df_selected_mediaID['mediaID'].values[0], '1' ))    
#     st.button('👎', key=random(), on_click=t.activity, args=(df_selected_mediaID['mediaID'].values[0], '-1'))    

# # Depreciated
# with st.expander("Jaccard Distance NER from this episode"):
#     t.tiles(LC.get_top_k_ner_jaccard(df_NPO, st.session_state['mediaID'], 6))