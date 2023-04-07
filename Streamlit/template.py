import streamlit as st
from random import random
import json
import datetime

DEBUG = False

# save the activities as a file
def save_activities():
    with open('data/activities.json', 'w') as outfile:
        json.dump(st.session_state['activities'], outfile)

# function that processes the userfeedback activity
def activity(id, activity):
    data = {'content_id': id, 'rating': st.session_state['rating'], 'user_id': st.session_state['user'], 'datetime': str(datetime.datetime.now())}
    if DEBUG:
        print(f"template.py activity() line 13: {data}")
    st.session_state['activities'].append(data)
    save_activities()

# set mediaID, show, and season session state
def select_episode(e):
    st.session_state['mediaID'] = e['mediaID']
    st.session_state['mainTitle'] = e['mainTitle']
    st.session_state['season'] = e['season']
    pass

# Set and media item to a time
def tile_item(column, item):
    with column:
        # Some shows do not have an image, use the very pyhtonic "Try and see if it fails" method
        try:
            st.image(item['thumbnail'], use_column_width='always')
        except st.runtime.media_file_storage.MediaFileStorageError:
            st.image("no-image.png", use_column_width='always')
        st.markdown(item['mainTitle'])
        st.caption(item['longSummary'][:50] + (item['longSummary'][50:] and '..'))
        st.button('▶', key=random(), on_click=select_episode, args=(item, ))

# make tiles next to each other and fillthese with shows.
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