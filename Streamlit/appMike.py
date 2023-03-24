import streamlit as st
import pandas as pd
import templatemike as t
import authenticate as a
import json
from itertools import cycle
from random import random
import liveCalc as LC
import searchResults as SR
import numpy as np

search_bar_placeholder_text = "zoeken"

st.set_page_config(layout="wide")
df_NPO = pd.read_csv("NPO_mike.csv")
df_NPO[df_NPO["thumbnail"].isna()] = "no-image.png"
df_NPO[df_NPO["longSummary"].isna()] = ""
df_NPO['mainTitle'] = df_NPO['mainTitle'].str.lower()
df_NPO['mainTitle'] = df_NPO['mainTitle'].fillna('')
# the simpsons episodes
df = pd.read_json('episodes.json')

df_users = pd.read_json('users.json')

# open the activities json file
with open('activities.json') as json_file:
    users_activities = json.load(json_file)

# create a session state
if 'user' not in st.session_state:
    st.session_state['user'] = LC.generate_random_userID(10)

if 'activities' not in st.session_state:
    st.session_state['activities'] = users_activities

if 'show' not in st.session_state:
    st.session_state['show'] = '1 euro per gesprek'

if 'episode' not in st.session_state:
    st.session_state['episode'] = 'POW_05260990'

if 'search' not in st.session_state:
    st.session_state['search'] = search_bar_placeholder_text

if 'df_NPO' not in st.session_state:
    st.session_state['df_NPO'] = df_NPO

# # uncommenten en dan kunnen we als we willen authenticatie weer aanzetten 
# authenticate
# a.authenticate()

# retrieve  initial mediaID from session state and pick the first season
df_selected_show = df_NPO[df_NPO['mainTitle'] == st.session_state['show']]
season = min(df_selected_show['season'])
################################################
# Shown on page:
################################################
# search function
usersearch = st.text_input('Series title', search_bar_placeholder_text)
search_result = df_NPO[df_NPO['mainTitle'].str.contains(usersearch.lower())]
if usersearch == 'zoeken':
    df_selected_show = df_NPO[df_NPO['mainTitle'] == '1 euro per gesprek']
elif not search_result.empty:
    df_selected_show = search_result
else:
    st.write("No results found.")
    df_selected_show = df_NPO[df_NPO['mainTitle'] == '1 euro per gesprek']
# finding available seasons and episode of searched show

available_seasons = df_selected_show['season'].unique()
available_episodes = df_selected_show['episode'].loc[(df_selected_show['season'] == season)]
available_episodes
episode_amount = available_episodes.count()
episode_amount
df_selected_show
chosen_episode = df_selected_show[df_selected_show['mediaID']==st.session_state['episode']]
chosen_episode
col1, col2 = st.columns(2)
# image of the show
with col1:
    st.image(str(chosen_episode['thumbnail'].values[0]), use_column_width='always',output_format="JPEG")
# information about the show
with col2:
    st.title(chosen_episode['mainTitle'].values[0])
    st.caption(chosen_episode['broadcaster'].values[0])
    st.markdown(chosen_episode['longSummary'].values[0])
season = st.selectbox('Select a season:', available_seasons)

with st.expander("Episodes in this season"):
  t.tiles(df_selected_show)
# 
"""
if(usersearch != search_bar_placeholder_text and usersearch != ""):
    with st.expander("search", expanded=True):
        t.tiles(SR.get_search_result(df_NPO ,usersearch, 5))
"""

"""
with st.expander('Implicit and Explicit feedback'):
    st.button('👍', key=random(), on_click=t.activity, args=(df_selected_mediaID['mediaID'].values[0], 'Like' ))    
    st.button('👎', key=random(), on_click=t.activity, args=(df_selected_mediaID['mediaID'].values[0], 'Dislike'))    

with st.expander("Jaccard Distance NER from this episode"):
    t.tiles(LC.get_top_k_ner_jacqard(df_NPO, st.session_state['mediaID'], 6))
"""
