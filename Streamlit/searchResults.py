import pandas as pd
import json
import liveCalc as LC

# open tokenined titles
with open('data/mediaID_MainTitleTokens.json') as json_file:
    tokenizedTitles = json.load(json_file)


def jaccard_score_for_search(searchtext_tokenized)-> list[list[str, float]]:
    """
    Get the jaccard score between all mainTitle's and the search query from the user.
    """
    simularity_score = []
    for mediaID, tokens in tokenizedTitles.items():
        simularity = LC.jaccard_similarity(searchtext_tokenized ,tokens)
        simularity_score.append([mediaID, simularity])        
    return simularity_score


def tokenize(text:str)->list[str]:
    """
    Tokenize text
    """
    return text.lower().split(" ")


def get_search_result(df, searchtext:str, n_results=5)->pd.DataFrame:
    searchtext_tokenized = tokenize(searchtext)
    jaccard_scores_list = jaccard_score_for_search(searchtext_tokenized)
    jaccard_scores_df = pd.DataFrame(jaccard_scores_list, columns=['mediaID','jaccard_score']).sort_values(by='jaccard_score', ascending=False)
    search_results = pd.merge(left=jaccard_scores_df, right=df, left_on='mediaID', right_on="mediaID", how="inner")
    return search_results.head(n_results)