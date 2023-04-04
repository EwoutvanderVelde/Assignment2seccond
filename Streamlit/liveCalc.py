import pandas as pd
import json
import random
import string
import streamlit as st

DEBUG = False


""" DEPRECIATED
with open('data/miediaID_NERTags.json', 'r') as fp:
    media_tag_dict = json.load(fp)
""" 

def generate_random_userID(length):
    """
    Generate a rondom string of length n as an "unique" identifier for the user
    """
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))


def jaccard_similarity(mediaID_tags_a:list[str], mediaID_tags_b:list[str])->float:
    """
    Standard jaccard simularity function for lists of string (but should word with numbers)
    """
    set_tags_a = set(mediaID_tags_a)
    set_tags_b = set(mediaID_tags_b)
    
    union = set_tags_a.union(set_tags_b)
    intersection = set_tags_a.intersection(set_tags_b)
    if len(union) != 0: #  Zero devision
        return float(len(intersection)) / float(len(union))
    else:
        return 0

""" Depreciated
# get kaccard_similarity all other mediaID's
def get_jaccard_similarity_list(mediaID:str)->list[list[str, float]]:
    tags = media_tag_dict[mediaID]
    distancelist = []
    for key, value in media_tag_dict.items():
        distance = jaccard_similarity(tags ,value)
        distancelist.append([key, distance])        
    return distancelist
"""

def max_n_reccomendation_per_broadcaster(df:pd.DataFrame, max_n:int = 2)->pd.DataFrame:
    """
    Filter function to smooth the recommendations. Use this function to get only n recommendations per broadcaster
    """
    broadcastcounter = {}
    def check_if_double(broadcaster:str):
        if broadcaster not in broadcastcounter.keys():
            broadcastcounter[broadcaster] = 1
            return True
        elif broadcastcounter[broadcaster] < max_n:
            broadcastcounter[broadcaster] += 1
            return True
        else:
            return False
        
    # We make a copy just in case
    df_copy = df.copy()
    df_copy["keep"] = df_copy["broadcaster"].apply(lambda x: check_if_double(x))    
    
    # Drop the keep column for consistency
    result = df_copy[df_copy["keep"]==True].drop(columns= ["keep"])
    return result 

""" Depreciated
def get_top_k_ner_jaccard(df:pd.DataFrame, mediaID:str, topk:int=10, exclude_current_broadcaster=True, no_repeat=True)-> pd.DataFrame:
    jaccard_similarity_list = get_jaccard_similarity_list(mediaID)
    jaccard_similarity_df = pd.DataFrame(jaccard_similarity_list, columns=['mediaID','jaccard_score']).sort_values(by='jaccard_score', ascending=False)
    df_merged_jaccard_score = pd.merge(left=jaccard_similarity_df, right=df, left_on='mediaID', right_on="mediaID", how="inner")
    
    # if we want to exclude recommendations for the broadcaster the user is already watching
    if exclude_current_broadcaster:
        broadcaster_to_exclude = df.query(f"mediaID == '{mediaID}'")["broadcaster"].values[0]
        df_merged_jaccard_score.query(f"broadcaster != '{broadcaster_to_exclude}'", inplace=True)
    
    # if we want to exclude multiple repetations of the same broadcaster
    if no_repeat:
        df_merged_jaccard_score = max_n_reccomendation_per_broadcaster(df_merged_jaccard_score, max_n=2)
    
    return df_merged_jaccard_score.head(topk)
"""

def get_similar_content(df, mediaID):
    """
    returns dataframe where content is has the same topic as mediaID
    """
    topic = df[df['mediaID'] == mediaID]['Topic'].values[0]
    if DEBUG:
        print(f"liveCalc.py get_similar_content topic: {topic}")
    return df[df['Topic'] == topic]


def getRecommendations(df:pd.DataFrame, mediaID:str, topk:int=10, exclude_current_broadcaster=True, no_repeat=True)->pd.DataFrame:
    """
    Return a dataframe with recommendations. Depending if the user has already rated content,
    it will either return content based recommendations, or a combination of content and collaberative based recommendations.
    """
    
    content_based_recommendations = get_similar_content(df, mediaID)
    content_based_recommendations = content_based_recommendations[content_based_recommendations["mediaID"] != mediaID]
    
    user_based_recommendations = st.session_state['userRecommendations']
    
    if user_based_recommendations is None:
        all_results = max_n_reccomendation_per_broadcaster(content_based_recommendations)
        topk = min(topk, len(all_results))
        return all_results.sample(topk, replace=False)
    else:
        in_both = pd.merge(content_based_recommendations, user_based_recommendations[["mediaID", "userPrediction"]]).sort_values('userPrediction', ascending= False)
        if (len(in_both) < topk):
            n_to_add = topk - len(in_both)
            in_both = pd.concat([in_both, user_based_recommendations[user_based_recommendations["mediaID"] != mediaID]], axis = 0, ignore_index=True)
        all_results = max_n_reccomendation_per_broadcaster(in_both, max_n=2)
        topk = min(topk, len(all_results))
        result = all_results.head(topk)
        return result