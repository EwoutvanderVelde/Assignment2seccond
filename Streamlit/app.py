import streamlit as st
import pandas as pd
import template as t
import authenticate as a
import json
from itertools import cycle
from random import random
import liveCalc as LC
import searchResults as SR
import numpy as np

search_bar_placeholder_text = "zoeken"

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

# # uncommenten en dan kunnen we als we willen authenticatie weer aanzetten 
# authenticate
# a.authenticate()

# retrieve mediaID from session state
df_selected_mediaID = df_NPO[df_NPO['mediaID'] == st.session_state['mediaID']]

################################################
# Shown on page:
################################################

userseach = st.text_input('Movie title', search_bar_placeholder_text)

col1, col2 = st.columns(2)
with col1:
    st.image(str(df_selected_mediaID['thumbnail'].values[0]), use_column_width='always',output_format="JPEG")

with col2:
    st.title(df_selected_mediaID['mainTitle'].values[0])
    st.caption(df_selected_mediaID['broadcaster'].values[0])
    st.markdown(df_selected_mediaID['longSummary'].values[0])
    st.caption('Season ' + str(df_selected_mediaID['subTitle'].values[0]) + ' | episode ' + str(df_selected_mediaID['subTitle'].values[0]) + ' | Recomendations: ' + str(LC.get_top_k_ner_jacqard(df_NPO, st.session_state["mediaID"])['mediaID']))

if(userseach != search_bar_placeholder_text and userseach != ""):
    with st.expander("search", expanded=True):
        t.tiles(SR.get_search_result(df_NPO ,userseach, 5))



with st.expander('Implicit and Explicit feedback'):
    st.button('👍', key=random(), on_click=t.activity, args=(df_selected_mediaID['mediaID'].values[0], 'Like' ))    
    st.button('👎', key=random(), on_click=t.activity, args=(df_selected_mediaID['mediaID'].values[0], 'Dislike'))    

with st.expander("Jaccard Distance NER from this episode"):
    t.tiles(LC.get_top_k_ner_jacqard(df_NPO, st.session_state['mediaID'], 6))

