import pandas as pd
import json
import random
import string

def generate_random_userID(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


with open('miediaID_NERTags.json', 'r') as fp:
    media_tag_dict = json.load(fp)

def jaccard_distance(user_ids_isbn_a, user_ids_isbn_b):
                
    set_isbn_a = set(user_ids_isbn_a)
    set_isbn_b = set(user_ids_isbn_b)
    
    union = set_isbn_a.union(set_isbn_b)
    intersection = set_isbn_a.intersection(set_isbn_b)
        
    return len(intersection) / float(len(union))
# code goes here
def get_jaccard_distances(mediaID):
    tags = media_tag_dict[mediaID]
    distancelist = []
    for key, value in media_tag_dict.items():
        distance = jaccard_distance(tags ,value)
        distancelist.append([key, distance])
        
    return distancelist


def remove_repeating_items(df:pd.DataFrame, max_iter:int)->pd.DataFrame:
    broadcastcount = {}
    def check_if_double(broadcaster:str):
        if broadcaster not in broadcastcount.keys():
            broadcastcount[broadcaster] = 1
            return True
        elif broadcastcount[broadcaster] <= max_iter:
            broadcastcount[broadcaster] += 1
            return True
        else:
            return False
    temp_df = df.copy()
    temp_df["keep"] = df["broadcaster"].apply(lambda x: check_if_double(x))            
    #print(temp_df[temp_df["keep"]==True].drop('keep', inplace=True, axis=1))
    return temp_df[temp_df["keep"]==True]

def get_top_k_ner_jacqard(df, mediaID, topk = 10, excludeBC=True, no_repeat=True)-> pd.DataFrame:
    broadcastExclude = df.query(f"mediaID == '{mediaID}'")["broadcaster"].values[0]
    JSframe = (pd.DataFrame(get_jaccard_distances(mediaID), columns=['mediaID','JS']).sort_values(by='JS', ascending=False))
    result = pd.merge(left=JSframe, right=df, left_on='mediaID', right_on="mediaID", how="inner")
    print(result["JS"])
    if excludeBC:
        result.query(f"broadcaster != '{broadcastExclude}'", inplace=True)
    if no_repeat:
        result = remove_repeating_items(result, 2)
    return result.head(topk)

