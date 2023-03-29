import pandas as pd
import json
import numpy as np
import pickle
import streamlit as st

def renew_data_frames():
    df_activities = pd.read_json("data/activities.json")
    df_selected = df_activities[df_activities['rating'] != "no rating"]
    df_npo = pd.read_csv("data/NPO_mike.csv")
    return df_selected, df_npo

def get_user_row_from_df(df_selected:pd.DataFrame, userID:str)-> list[int]:
        return list(df_selected[df_selected['user_id'] == userID]['rating'].astype(np.float32))


def create_user_rating_row(df_selected, mediaIDList, index_userID, mediaID_index, userID):
    cols = (len(mediaIDList))
    user_ratings=np.zeros([1,cols], dtype=np.int8)
    # print(f"empy user rating list: {user_ratings}")
    for i, row in enumerate(user_ratings):  # For each user
        useractivities = df_selected[df_selected['user_id'] == userID]  
        for j in useractivities.iterrows():
            content_id = (j[1]["content_id"])
            columnindex = mediaID_index[content_id]
            row[columnindex] = int(j[1]["rating"])
            # print(f"score {row[columnindex]} at {columnindex}")
    return user_ratings

def get_distance_to_other_users(user_rating_matrix, user_mean_dict, userID, index_userID, userID_index, df_selected, mediaIDList, mediaID_index):
    #index_a does not exist normaly, except if user 
    try:
        index_a = userID_index[userID]
    except:
        index_a = -1
    
    row_a = create_user_rating_row(df_selected, mediaIDList, index_userID, mediaID_index, userID)[0]
    distance_dict = {}
    
    row_a_mean = np.mean(get_user_row_from_df(df_selected, userID))
    if len(row_a[row_a != 0]) >1:  # Avoid devision by zero lateron
        row_a_norm = [score-row_a_mean if score !=0 else 0 for score in row_a]
    else:
        row_a_norm = row_a
    
    for index_b, row_b in enumerate(user_rating_matrix):
        if index_a != index_b:
            row_b_mean = user_mean_dict[index_userID[index_b]]
            if len(row_b[row_b != 0] >1): # Avoid devision by zero lateron
                row_b_norm = [score-row_b_mean if score !=0 else 0 for score in row_b]
            else:
                row_b_norm = row_b
            distance_dict[index_userID[index_b]] = np.dot(row_a_norm, row_b_norm)/(np.linalg.norm(row_a_norm) * np.linalg.norm(row_b_norm))
    return distance_dict

def open_pickle(varname):
    with open(f'data/{varname}.pkl', 'rb') as fp:
        var = pickle.load(fp)
    return var
    
# old code
def renewPersonalRecomedations(current_user, df_npo):
    # Load all pre processed data
    df_selected, df_npo = renew_data_frames()
    userlist = open_pickle("userlist")
    mediaIDList = open_pickle("mediaIDList")
    userID_index, index_userID = open_pickle("userID_index"), open_pickle("index_userID")
    mediaID_index, index_mediaID = open_pickle("mediaID_index"), open_pickle("index_mediaID")
    user_rating_matrix = np.load('data/user_rating_matrix.npy')
    user_rating_mean = open_pickle("user_rating_mean")
    distance_to_other_users = get_distance_to_other_users(user_rating_matrix, user_rating_mean, current_user, index_userID, userID_index, df_selected, mediaIDList, mediaID_index)
    return distance_to_other_users


def test():
    df_selected, df_npo = renew_data_frames()
    print(renewPersonalRecomedations("zuiiztxxjt",df_npo))
    return

#test()
#renewPersonalRecomedations("teqocdjxcd", renew_data_frames())




