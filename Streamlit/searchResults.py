import pandas as pd
import json
import liveCalc as LC

# open tokenined titles
with open('data/mediaID_MainTitleTokens.json') as json_file:
    tokenizedTitles = json.load(json_file)


def jaccard_score_for_search(searchtext_tokenized)-> list[list[str, float]]:
    distancelist = []
    for mediaID, tokens in tokenizedTitles.items():
        distance = LC.jaccard_similarity(searchtext_tokenized ,tokens)
        distancelist.append([mediaID, distance])        
    return distancelist


def get_search_result(df, searchtext:str, n_results=5)->pd.DataFrame:
    searchtext_tokenized = searchtext.lower().split(" ")
    jaccard_scores_list = jaccard_score_for_search(searchtext_tokenized)
    jaccard_scores_df = pd.DataFrame(jaccard_scores_list, columns=['mediaID','jaccard_score']).sort_values(by='jaccard_score', ascending=False)
    df_merge_jaccard_scores = pd.merge(left=jaccard_scores_df, right=df, left_on='mediaID', right_on="mediaID", how="inner")
    return df_merge_jaccard_scores.head(n_results)