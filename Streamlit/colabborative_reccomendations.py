import pandas as pd
import json
import numpy as np
import pickle
import streamlit as st


def open_pickle(varname):
    with open(f'data/{varname}.pkl', 'rb') as fp:
        var = pickle.load(fp)
    return var

def renew_data_frames():
    df_activities = pd.read_json("data/activities.json")
    df_selected = df_activities[df_activities['rating'] != "no rating"]
    return df_selected

def get_user_row_from_df(df_selected:pd.DataFrame, userID:str)-> list[int]:
        return list(df_selected[df_selected['user_id'] == userID]['rating'].astype(np.float32))

def create_user_rating_row(df_selected, mediaIDList, index_userID, mediaID_index, userID):
    cols = (len(mediaIDList))
    user_ratings=np.zeros([1,cols], dtype=np.int8)
    for i, row in enumerate(user_ratings):  # For each user
        useractivities = df_selected[df_selected['user_id'] == userID]  
        for j in useractivities.iterrows():
            content_id = (j[1]["content_id"])
            columnindex = mediaID_index[content_id]
            row[columnindex] = int(j[1]["rating"])
    return user_ratings


def get_simularity_to_other_users(user_rating_matrix, user_mean_dict, userID, index_userID, userID_index, df_selected, mediaIDList, mediaID_index):
    #index_a does not exist normaly, except if user 
    try:
        index_a = userID_index[userID]
    except:
        index_a = -1
    
    row_a = create_user_rating_row(df_selected, mediaIDList, index_userID, mediaID_index, userID)[0]
    simularity_dict = {}
    
    if len(row_a[row_a != 0]) >1: # Avoid devision by zero lateron
        row_a_mean = np.mean(get_user_row_from_df(df_selected, userID))
    else:
        row_a_mean = 0
    row_a_norm = [score-row_a_mean if score !=0 else 0 for score in row_a]

    for index_b, row_b in enumerate(user_rating_matrix):
        if index_a != index_b:
            row_b_mean = user_mean_dict[index_userID[index_b]]
            if len(row_b[row_b != 0] >1): # Avoid devision by zero lateron
                row_b_norm = [score-row_b_mean if score !=0 else 0 for score in row_b]
            else:
                row_b_norm = row_b
            simularity_dict[index_userID[index_b]] = np.dot(row_a_norm, row_b_norm)/(np.linalg.norm(row_a_norm) * np.linalg.norm(row_b_norm))
    return simularity_dict, row_a_mean


def sort_simularitys(simularitys:dict)->dict:
    return dict(sorted(simularitys.items(), key=lambda x:x[1]))


def userItemPrediction(df_selected, simularity_to_other_users, current_user_mean, user_rating_matrix, mediaID_index, index_mediaID, userID_index, max_neighbourhood = 5):
    sorted_simularitys = sort_simularitys(simularity_to_other_users)
    
    if len(sorted_simularitys) < max_neighbourhood:
        neighbours = sorted_simularitys
    else:
        neighbours = sorted_simularitys[:max_neighbourhood]

    unique_mediaID = df_selected[df_selected['user_id'].isin(neighbours.keys())]["content_id"].unique()
    recommendations = {}
    for mediaID in unique_mediaID:
        matrix_mediaID_index = mediaID_index[mediaID]
        numerator = 0
        denominator = 0        
        for userID, simularity in neighbours.items():
            numerator += simularity*user_rating_matrix[userID_index[userID], matrix_mediaID_index]
            denominator += simularity
        recommendations[mediaID] = current_user_mean + (numerator/denominator)

    return recommendations


# old code
def renewPersonalRecomedations(current_user, df_npo):
    # Load all pre processed data
    df_selected = renew_data_frames()
    userlist = open_pickle("userlist")
    mediaIDList = open_pickle("mediaIDList")
    userID_index, index_userID = open_pickle("userID_index"), open_pickle("index_userID")
    mediaID_index, index_mediaID = open_pickle("mediaID_index"), open_pickle("index_mediaID")
    user_rating_matrix = np.load('data/user_rating_matrix.npy')
    user_rating_mean = open_pickle("user_rating_mean")
    
    simularity_to_other_users, current_user_mean = get_simularity_to_other_users(user_rating_matrix, user_rating_mean, current_user, index_userID, userID_index, df_selected, mediaIDList, mediaID_index)
    predictions = userItemPrediction(df_selected, simularity_to_other_users, current_user_mean, user_rating_matrix, mediaID_index, index_mediaID, userID_index)
    
    # nog kiezen welke handiger is...
    st.session_state['userRecommendations'] = df_npo[df_npo["mediaID"].isin(predictions.keys())]
    #st.session_state['userRecommendations'] = predictions

    return predictions


def test():
    df_selected, df_npo = renew_data_frames()
    print(renewPersonalRecomedations("zuiiztxxjt",df_npo))
    return

#test()
#renewPersonalRecomedations("teqocdjxcd", renew_data_frames())




