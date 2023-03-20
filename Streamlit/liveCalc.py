import pandas as pd
import json

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

def get_top_k_ner_jacqard(df, mediaID, topk = 10)-> pd.DataFrame:
    broadcastExclude = df.query(f"mediaID == '{mediaID}'")["broadcaster"].values[0]
    temp = (pd.DataFrame(get_jaccard_distances(mediaID), columns=['mediaID','JS']).sort_values(by='JS', ascending=False))
    merged = pd.merge(left=temp, right=df, left_on='mediaID', right_on="mediaID", how="inner")
    return merged.query(f"broadcaster != '{broadcastExclude}'").head(topk)

#def get_n_recommendation()