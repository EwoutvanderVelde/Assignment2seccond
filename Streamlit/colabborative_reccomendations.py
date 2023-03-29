import pandas as pd
import json
import numpy as np

def renew_data_frames():
    df_activities = pd.read_json("data/activities.json")
    df_selected = df_activities[df_activities['activity'] == "Select mediaID"]
    df_npo = pd.read_csv("data/NPO_mike.csv")
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
            row[columnindex] += 1

    return user_ratings

def get_user_mean(matrix:np.ndarray, index_userID:dict)-> dict:
    usermean = {}
    for i in range(len(matrix)):
        usermean[index_userID[i]] = 1/np.mean(matrix[i][matrix[i] != 0])
    return usermean

def get_distance_to_other_users(user_rating_matrix, user_mean_dict, userID, index_userID, userID_index):
    index_a = userID_index[userID]
    row_a = user_rating_matrix[index_a]
    distance_dict = {}
    row_a_norm = row_a - user_mean_dict[index_userID[index_a]]  # if not binary
    row_a_norm = row_a  # if binary
    for index_b, row_b in enumerate(user_rating_matrix):
        if index_a != index_b:
            row_b_norm = row_b - user_mean_dict[index_userID[index_b]]  # if not binary
            row_b_norm = row_b  # if binary
            #dot = (np.dot(row_a_norm, row_b_norm))
            #length = (np.linalg.norm(row_a_norm) * np.linalg(row_b_norm))
            #print(length)
            distance_dict[index_userID[index_b]] = np.dot(row_a_norm, row_b_norm)/(np.linalg.norm(row_a_norm) * np.linalg.norm(row_b_norm))
    return distance_dict

def renewPersonalRecomedations(current_user, user_activities, df_npo):
    df_selected, df_npo = renew_data_frames()

    userlist = get_unique_users(df_selected)
    mediaIDList = get_unique_mediaIDs(df_npo)
    userID_index, index_userID = create_name_index_dict(userlist)
    mediaID_index, index_mediaID = create_name_index_dict(mediaIDList)

    user_rating_matrix = create_user_rating_matrix(df_selected, df_npo, userlist, mediaIDList, index_userID, mediaID_index)
    user_rating_mean = get_user_mean(user_rating_matrix, index_userID)
    distance_to_other_users = get_distance_to_other_users(user_rating_matrix, user_rating_mean, current_user, index_userID, userID_index)
    
    return distance_to_other_users


#renewPersonalRecomedations("teqocdjxcd", renew_data_frames())




