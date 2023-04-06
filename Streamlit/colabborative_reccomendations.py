"""
This code generates user specific predictions for content not watched
Note everything is in functions to not run code unneccesaroly when loading in this file
"""

import pandas as pd
import numpy as np
import pickle
import streamlit as st
DEBUG = False


def open_pickle(varname):
    """
    Function to open pickle files, we will open a lot of them...
    """
    with open(f'data/{varname}.pkl', 'rb') as fp:
        var = pickle.load(fp)
    return var


def renew_data_frames():
    """
    Load the activities data again to make sure we have the latest data.
    """
    df_activities = pd.read_json("data/activities.json")
    df_ratings = df_activities[df_activities['rating'] != "no rating"]

    if DEBUG:
        print(f"collabFilter.py renew_data_drames df_ratings: {df_ratings}")
    
    return df_ratings


def get_user_ratings_from_df(df_ratings:pd.DataFrame, userID:str)-> list[int]:
    """
    Get all the ratings from the current user in list format
    """
    if DEBUG:
        print(f"collabFilter.py get_user_ratings_from_df df_ratings[df_ratings['user_id'] == userID]['rating']: \n{df_ratings[df_ratings['user_id'] == userID]['rating']}\n")
    
    return df_ratings[df_ratings['user_id'] == userID]

def get_mean_user_ratings(df_ratings:pd.DataFrame, userID:str)-> list[int]:
    """
    Get all the ratings from the current user in list format
    """
    mean = np.mean(list(get_user_ratings_from_df(df_ratings, userID)['rating'].astype(np.float32)))
    if DEBUG:
        print(f"collabFilter.py get_mean_user_ratings mean: {mean}")

    return mean


def create_user_rating_row(df_ratings, mediaIDList, mediaID2index, userID):
    """
    Get the user rating in matrix form
    Since we are looking at 1 user, this is of the for 1 x len(unique_media)
    Row is needed to calculate simularity to other users.
    """
    ncols = (len(mediaIDList))
    own_ratings=np.zeros([1,ncols], dtype=np.int8)  # np.int8 is to save some memory
    
    if DEBUG:
        print(f"collabFilter.py create_user_rating_row userID: {userID}")
        print(f"collabFilter.py create_user_rating_row user_ratings: {own_ratings}")
        print(f"collabFilter.py create_user_rating_row type(user_ratings): {type(own_ratings)}")
        print(f"collabFilter.py create_user_rating_row user_ratings.shape: {own_ratings.shape}")

    for i, row in enumerate(own_ratings):  # For each user
        current_user_ratings = df_ratings[df_ratings['user_id'] == userID]  
        for j in current_user_ratings.iterrows():
            mediaID = (j[1]["content_id"])
            columnindex = mediaID2index[mediaID]
            row[columnindex] = int(j[1]["rating"])
    
    if DEBUG:
        print(f"collabFilter.py create_user_rating_row user_ratings_filled: {own_ratings}")
        print(f"collabFilter.py create_user_rating_row type(user_ratings_filled): {type(own_ratings)}")
        print(f"collabFilter.py create_user_rating_row user_ratings_filled.shape: {own_ratings.shape}")
    
    return own_ratings[0]


def get_simularity_to_other_users(user_rating_matrix, user_mean_dict, userID, index2userID, userID2index, df_ratings, mediaIDList, mediaID2index):
    """
    Calculate how simulair our user is to other users in the database that we have from other users
    """
    
    # If current user has not made any recommendations yes, we can not find him in our dict
    try:
        index_current_user = userID2index[userID]
    except:
        index_current_user = -1
    
    row_current_user = create_user_rating_row(df_ratings, mediaIDList, mediaID2index, userID)

    if DEBUG:
        print(f"collabFilter.py get_simularity_to_other_users row_current_user: {row_current_user}")
        print(f"collabFilter.py get_simularity_to_other_users type(row_current_user): {type(row_current_user)}")
        print(f"collabFilter.py get_simularity_to_other_users row_current_user.shape: {row_current_user.shape}")

    # We are gonna substract the mean of eacht user from their ratings, 
    # if a user only has 1 rating, their new score would become 0, this can become problamatic.
    # Of user only has one rating, set their mean to 0
    if len(row_current_user[row_current_user != 0]) >1: 
        row_current_user_mean = get_mean_user_ratings(df_ratings, userID)
    else:
        row_current_user_mean = 0

    row_current_user_normalized = [score-row_current_user_mean if score !=0 else 0 for score in row_current_user]
    simularity_dict = {}

    for index_other_user, row_other_user in enumerate(user_rating_matrix):
        if index_current_user != index_other_user:
            row_other_user_mean = user_mean_dict[index2userID[index_other_user]]
            
            # ckeck if other users have more than 1 rating
            if len(row_other_user[row_other_user != 0] >1): # Avoid devision by zero lateron
                row_other_user_normalized = [score-row_other_user_mean if score !=0 else 0 for score in row_other_user]
            else:
                row_other_user_normalized = row_other_user

            numerator = np.dot(row_current_user_normalized, row_other_user_normalized)
            denomenator = (np.linalg.norm(row_current_user_normalized) * np.linalg.norm(row_other_user_normalized))
            
            # We still sometimes get a division by zero, not sure why
            if denomenator != 0:
                simularity = numerator/denomenator
            else: 
                simularity=0

            simularity_dict[index2userID[index_other_user]] = simularity
    print(f"collabFilter.py get_simularity_to_other_users index2userID:{index2userID}")
    #print(f"collabFilter.py get_simularity_to_other_users row_current_user_mean:{row_current_user_mean}")
    #print(f"collabFilter.py get_simularity_to_other_users row_current_user_mean:{row_current_user_mean}")
    print(f"collabFilter.py get_simularity_to_other_users simularity_dict_filled:{simularity_dict}")
    print(f"collabFilter.py get_simularity_to_other_users row_current_user_mean:{row_current_user_mean}")
    return simularity_dict, row_current_user_mean


def sort_simularities(simularities:dict)->dict:
    """
    Name is somewhat self explenetory
    """
    return dict(sorted(simularities.items(), key=lambda x:x[1]))


def userItemPrediction(df_ratings, simularity_to_other_users, current_user_mean, user_rating_matrix, mediaID2index, userID2index, max_neighbourhood = 50)->dict:
    """
    Predict rating for current user
    """

    # Get the n most simulair users (neighbours)
    sorted_simularities = sort_simularities(simularity_to_other_users)
    if len(sorted_simularities) < max_neighbourhood:
        neighbours = sorted_simularities
    else:
        neighbours = sorted_simularities[:max_neighbourhood]

    # We only want to make predictions for which we know a rating from other users
    unique_mediaID = df_ratings[df_ratings['user_id'].isin(neighbours.keys())]["content_id"].unique()

    # Use the formula on slides week 6
    recommendations = {}
    for mediaID in unique_mediaID:
        matrix_mediaID_index = mediaID2index[mediaID]
        numerator = 0
        denominator = 0        
        for userID, simularity in neighbours.items():
            if((user_rating:= user_rating_matrix[userID2index[userID], matrix_mediaID_index]) != np.nan):
                numerator += simularity*user_rating
                denominator += simularity
        recommendations[mediaID] = current_user_mean + (numerator/denominator)
    return recommendations


def renewPersonalRecomedations(current_user, df_npo)->pd.DataFrame:
    """
    Function called from streamlit button. Will return a dataframe with shows that simular users watch.
    """
    # Load all pre processed data
    df_ratings = renew_data_frames()
    userlist = open_pickle("userlist")
    mediaIDList = open_pickle("mediaIDList")
    userID2index, index2userID = open_pickle("userID_index"), open_pickle("index_userID")
    mediaID2index, index2mediaID = open_pickle("mediaID_index"), open_pickle("index_mediaID")
    user_rating_matrix = np.load('data/user_rating_matrix.npy')
    user_rating_mean = open_pickle("user_rating_mean")
    
    simularity_to_other_users, current_user_mean = get_simularity_to_other_users(user_rating_matrix, user_rating_mean, current_user, index2userID, userID2index, df_ratings, mediaIDList, mediaID2index)
    predictions = userItemPrediction(df_ratings, simularity_to_other_users, current_user_mean, user_rating_matrix, mediaID2index, userID2index)
    
    # Get the dataframe entries from our recommendations and add prediction score
    result = df_npo[df_npo["mediaID"].isin(predictions.keys())]
    result['userPrediction'] = result['mediaID'].apply(lambda x: predictions[x])
    st.session_state['userRecommendations'] = result

    return result



def test(df_npo):
    """
    Function used to test the script without using streamlit
    """
    df_selected = renew_data_frames()
    print(f'-------------------------RESULT --------------------------------- \n {renewPersonalRecomedations("zuiiztxxjt",df_npo)}')
    return


# Only run when we are debugging, this does not run when script is imported
if __name__ == "__main__":
    # Calling functions to test
    DEBUG = True
    test(pd.read_csv("data/NPOPlayerv2.csv"))




