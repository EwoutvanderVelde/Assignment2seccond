import pandas as pd
import json
import random
import string
import streamlit as st

""" DEPRECIATED
with open('data/miediaID_NERTags.json', 'r') as fp:
    media_tag_dict = json.load(fp)
""" 
# Used to generate a random string as an "unique" identifier for the user
def generate_random_userID(length):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))


# standard jaccard_similarity function
def jaccard_similarity(mediaID_tags_a:list[str], mediaID_tags_b:list[str])->float:
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

# filter function to even out the recommendations. Use this function to get only n recommendations per broadcaster
def max_n_reccomendation_per_broadcaster(df:pd.DataFrame, max_n:int = 2)->pd.DataFrame:
    broadcastcount = {}
    def check_if_double(broadcaster:str):
        if broadcaster not in broadcastcount.keys():
            broadcastcount[broadcaster] = 1
            return True
        elif broadcastcount[broadcaster] < max_n:
            broadcastcount[broadcaster] += 1
            return True
        else:
            return False
    df_copy = df.copy()  # Make a copy, since in the next step we create a column, and we do not want to modify the original one
    df_copy["keep"] = df_copy["broadcaster"].apply(lambda x: check_if_double(x))            
    return df_copy[df_copy["keep"]==True].drop(columns= ["keep"])  # Drop the keep column for consistency

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
    topic = df[df['mediaID'] == mediaID]['Topic'].values[0]
    return df[df['Topic'] == topic]

def getRecommendations(df:pd.DataFrame, mediaID:str, topk:int=10, exclude_current_broadcaster=True, no_repeat=True)->pd.DataFrame:
    content_based_recommendations = get_similar_content(df, mediaID)
    content_based_recommendations = content_based_recommendations[content_based_recommendations["mediaID"] != mediaID]
    user_based_recommendations = st.session_state['userRecommendations']
    if user_based_recommendations is None:
        return max_n_reccomendation_per_broadcaster(content_based_recommendations).sample(topk, replace=False)
    else:
        in_both = pd.merge(content_based_recommendations, user_based_recommendations[["mediaID", "userPrediction"]]).sort_values('userPrediction', ascending= False)
        if (len(in_both) < topk):
            n_to_add = topk - len(in_both)
            in_both = in_both.append(user_based_recommendations[user_based_recommendations["mediaID"] != mediaID])

        result = max_n_reccomendation_per_broadcaster(in_both, max_n=2).head(topk)

        return result