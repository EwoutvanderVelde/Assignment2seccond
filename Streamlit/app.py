import streamlit as st
import pandas as pd
import template as t
import authenticate as a
import json
from itertools import cycle
from random import random
import liveCalc as LC
import numpy as np

st.set_page_config(layout="wide")
df_NPO = pd.read_csv("NPOPlayer.csv", sep=";")
df_NPO[df_NPO["thumbnail"].isna()] = "no-image.png"
df_NPO[df_NPO["longSummary"].isna()] = ""
# the simpsons episodes
df = pd.read_json('episodes.json')

df_users = pd.read_json('users.json')

# open the activities json file
with open('activities.json') as json_file:
    users_activities = json.load(json_file)

# create a session state
if 'season' not in st.session_state:
    st.session_state['season'] = 1

if 'episode' not in st.session_state:
    st.session_state['episode'] = 'tt0348034'

if 'user' not in st.session_state:
    st.session_state['user'] = LC.generate_random_userID(10)

if 'activities' not in st.session_state:
    st.session_state['activities'] = users_activities

if 'mediaID' not in st.session_state:
    st.session_state['mediaID'] = 'WO_POWN_8513746'

print(st.session_state['user'])
#authenticate
#a.authenticate()

# get seasons
seasons = pd.unique(df['season'].sort_values(ascending=True))

# retrieve season and episode from session state
df_season = df[df['season'] == st.session_state['season']]
#df_episode = df[df['id'] == st.session_state['episode']]
#print(df_NPO['mediaID'])
df_episode = df_NPO[df_NPO['mediaID'] == st.session_state['mediaID']]
#df_episode = df_episode.iloc[0]

col1, col2 = st.columns(2)
with col1:
    st.image(str(df_episode['thumbnail'].values[0]), use_column_width='always',output_format="JPEG")

with col2:
    st.title(df_episode['mainTitle'].values[0])
    st.caption(df_episode['broadcaster'].values[0])
    st.markdown(df_episode['longSummary'].values[0])
    st.caption('Season ' + str(df_episode['subTitle'].values[0]) + ' | episode ' + str(df_episode['subTitle'].values[0]) + ' | Recomendations: ' + str(LC.get_top_k_ner_jacqard(df_NPO, st.session_state["mediaID"])['mediaID']))

with st.expander('Implicit and Explicit feedback'):
    st.button('👍', key=random(), on_click=t.activity, args=(df_episode['mediaID'], 'Like' ))    
    st.button('👎', key=random(), on_click=t.activity, args=(df_episode['mediaID'], 'Dislike'))    

with st.expander("Jaccard Distance NER from this episode"):
    t.tiles(LC.get_top_k_ner_jacqard(df_NPO, st.session_state['mediaID'], 6))

