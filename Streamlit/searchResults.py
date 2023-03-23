import pandas as pd
import json
import liveCalc as LC

def jaccard_for_search(tokenizedTitles, searchtext_tokenized):
    distancelist = []
    for mediaID, tokens in tokenizedTitles.items():
        distance = LC.jaccard_similarity(searchtext_tokenized ,tokens)
        distancelist.append([mediaID, distance])        
    return distancelist


def get_search_result(df, searchtext:str, n_results=5)->pd.DataFrame:
    with open('mediaID_MainTitleTokens.json') as json_file:
        tokenizedTitles = json.load(json_file)
    searchtext_tokenized = searchtext.lower().split(" ")
    JSframe = (pd.DataFrame(jaccard_for_search(tokenizedTitles, searchtext_tokenized), columns=['mediaID','JS']).sort_values(by='JS', ascending=False))
    result = pd.merge(left=JSframe, right=df, left_on='mediaID', right_on="mediaID", how="inner")

    return result.head(n_results)