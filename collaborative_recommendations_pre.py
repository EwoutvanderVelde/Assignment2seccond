import pandas as pd
import json
import numpy as np
import pickle

def renew_data_frames():
    df_activities = pd.read_json("streamlit/data/activities.json")
    df_selected = df_activities[df_activities['rating'] != "no rating"]

    df_npo = pd.read_csv("streamlit/data/NPO_mike.csv")
    return df_selected, df_npo

def get_unique_users(df):
    return list(df["user_id"].unique())

def get_unique_mediaIDs(df):
    return list(df["mediaID"].unique())

def create_name_index_dict(names):
    names_to_index = {}
    index_from_names = {}
    for index, name in enumerate(names):
        names_to_index[name] = index
        index_from_names[index] = name
    return names_to_index, index_from_names

def create_empty_user_rating_matrix(userlist, mediaIDList):
    rows = (len(userlist))
    cols = (len(mediaIDList))
    empty_user_ratings=np.zeros([rows,cols], dtype=np.int8)
    return empty_user_ratings

def create_user_rating_matrix(df_selected, df_npo, userlist, mediaIDList, index_userID, mediaID_index):
    user_ratings = create_empty_user_rating_matrix(userlist, mediaIDList)
    
    for i, row in enumerate(user_ratings):  # For each user
        useractivities = df_selected[df_selected["user_id"] == index_userID[i]]  
        for j in useractivities.iterrows():
            content_id = (j[1]["content_id"])
            columnindex = mediaID_index[content_id]
            row[columnindex] = int(j[1]["rating"])

    return user_ratings

def get_user_mean(matrix:np.ndarray, index_userID:dict)-> dict:
    usermean = {}
    for i in range(len(matrix)):
        usermean[index_userID[i]] = np.mean(matrix[i][matrix[i] != 0])
    return usermean

def save_pickle(var, varname):
    with open(f'streamlit/data/{varname}.pkl', 'wb') as fp:
        pickle.dump(var, fp)
        print(f'{varname} saved successfully to file')

def create_new_user_rating_matrix():
    df_selected, df_npo = renew_data_frames()

    userlist = get_unique_users(df_selected)
    mediaIDList = get_unique_mediaIDs(df_npo)
    userID_index, index_userID = create_name_index_dict(userlist)
    mediaID_index, index_mediaID = create_name_index_dict(mediaIDList)

    user_rating_matrix = create_user_rating_matrix(df_selected, df_npo, userlist, mediaIDList, index_userID, mediaID_index)
    user_rating_mean = get_user_mean(user_rating_matrix, index_userID)
    print(user_rating_mean)
    np.save('streamlit/data/user_rating_matrix',user_rating_matrix)
    save_pickle(user_rating_mean, "user_rating_mean")
    save_pickle(userID_index, "userID_index")
    save_pickle(index_userID,"index_userID")
    save_pickle(mediaID_index,"mediaID_index")
    save_pickle(index_mediaID,"index_mediaID")
    save_pickle(mediaIDList,"mediaIDList")
    save_pickle(userlist,"userlist")
    print(np.shape(user_rating_matrix))



create_new_user_rating_matrix()