import streamlit as st
from random import random
import json
import datetime

# save the activities as a file
def save_activities():
    with open('data/activities.json', 'w') as outfile:
        json.dump(st.session_state['activities'], outfile)

# function that processes an activity
def activity(id, activity):
    data = {'content_id': id, 'activity': activity, 'user_id': st.session_state['user'], 'datetime': str(datetime.datetime.now())}
    print(data)
    # add to the session state
    st.session_state['activities'].append(data)
    # directly save the activities
    save_activities()

# set episode session state
def select_episode(e):
    st.session_state['mediaID'] = e['mediaID']
    st.session_state['show'] = e['mainTitle']
    st.session_state['season'] = e['season']
    activity(e['mediaID'], 'Select mediaID')

def tile_item(column, item):
    with column:
        try:
            st.image(item['thumbnail'], use_column_width='always')
        except st.runtime.media_file_storage.MediaFileStorageError:
            st.image("no-image.png", use_column_width='always')
        st.markdown(item['mainTitle'])
        st.caption(item['longSummary'][:50] + (item['longSummary'][50:] and '..'))
        
        #st.caption('Season ' + str(item['season']) + ' | episode ' + str(item['episode']) + ' | Rating ' + str(item['rating']) + ' | ' + str(item['votes']) + ' votes')
        st.button('▶', key=random(), on_click=select_episode, args=(item, ))

def tiles(df):
    # check the number of items
    nbr_items = df.shape[0]
    cols = nbr_items

    if nbr_items != 0:        
        # create columns with the corresponding number of items
        columns = st.columns(cols)
        # convert df rows to dict lists
        items = df.to_dict(orient='records')
        # apply tile_item to each column-item tuple (created with python 'zip')
        any(tile_item(x[0], x[1]) for x in zip(columns, items))