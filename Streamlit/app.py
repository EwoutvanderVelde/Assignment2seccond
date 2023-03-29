import streamlit as st
import pandas as pd
import template as t
import authenticate as a
import json
from itertools import cycle
from random import random
import liveCalc as LC
import searchResults as SR
import colabborative_reccomendations as CR
import numpy as np

search_bar_placeholder_text = "Zoeken..."

st.set_page_config(layout="wide")
#df_NPO = pd.read_csv("data/NPOPlayer.csv", sep=";")
df_NPO = pd.read_csv("data/NPO_mike.csv")

df_NPO[df_NPO["thumbnail"].isna()] = "no-image.png"
df_NPO[df_NPO["longSummary"].isna()] = ""

df_NPO['mainTitle'] = df_NPO['mainTitle'].fillna('')

# open the activities json file
with open('data/activities.json') as json_file:
    users_activities = json.load(json_file)

# create a session state
if 'user' not in st.session_state:
    st.session_state['user'] = LC.generate_random_userID(10)

if 'activities' not in st.session_state:
    st.session_state['activities'] = users_activities

if 'mediaID' not in st.session_state:
    st.session_state['mediaID'] = 'WO_POWN_8513746'

if 'search' not in st.session_state:
    st.session_state['search'] = search_bar_placeholder_text

if 'df_NPO' not in st.session_state:
    st.session_state['df_NPO'] = df_NPO

if 'show' not in st.session_state:
    st.session_state['show'] = df_NPO[df_NPO['mediaID'] == st.session_state['mediaID']]["mainTitle"].values[0]

if 'season' not in st.session_state:
    st.session_state['season'] = df_NPO[df_NPO['mediaID'] == st.session_state['mediaID']]["season"].values[0]

# # uncommenten en dan kunnen we als we willen authenticatie weer aanzetten 
# authenticate
# a.authenticate()

# retrieve mediaID from session state
df_selected_mediaID = df_NPO[df_NPO['mediaID'] == st.session_state['mediaID']]
df_selected_show = df_NPO[df_NPO['mainTitle'] == st.session_state['show']]
available_seasons = list(df_selected_show['season'].sort_values().unique())

################################################
# Shown on page:
################################################
st.session_state['user']
userdistance = st.button("Calculate new personal recommendations", key=random(), on_click=CR.renewPersonalRecomedations, args=(st.session_state['user'],users_activities, df_NPO))

userseach = st.text_input('Movie title', search_bar_placeholder_text)

season = st.selectbox('Select a season:', available_seasons, index=available_seasons.index(df_selected_mediaID['season'].values[0]))
available_episodes = df_selected_show.loc[(df_selected_show['season'] == season)]

col1, col2 = st.columns(2)
with col1:
    st.image(str(df_selected_mediaID['thumbnail'].values[0]), use_column_width='always',output_format="JPEG")

with col2:
    st.title(df_selected_mediaID['mainTitle'].values[0])
    st.caption(df_selected_mediaID['broadcaster'].values[0])
    st.markdown(df_selected_mediaID['longSummary'].values[0])
    st.caption('Season ' + str(df_selected_mediaID['mediaID'].values[0]) + ' | episode ' + str(df_selected_mediaID['subTitle'].values[0]) + ' | Recomendations: ' + st.session_state['show'])

if(userseach != search_bar_placeholder_text and userseach != ""):
    st.session_state['search'] = userseach
    with st.expander("search", expanded=True):
        t.tiles(SR.get_search_result(df_NPO ,userseach, 5))



with st.expander('Implicit and Explicit feedback'):
    st.button('👍', key=random(), on_click=t.activity, args=(df_selected_mediaID['mediaID'].values[0], '1' ))    
    st.button('👎', key=random(), on_click=t.activity, args=(df_selected_mediaID['mediaID'].values[0], '-1'))    

with st.expander("Jaccard Distance NER from this episode"):
    t.tiles(LC.get_top_k_ner_jaccard(df_NPO, st.session_state['mediaID'], 6))


rows = int(available_episodes.shape[0] / 10) +1
for i in range(rows):
    minrow = i*10
    maxrow = min(minrow + 10, available_episodes.shape[0])
    t.tiles(available_episodes.iloc[minrow:maxrow])