import pandas as pd
import json
import liveCalc as LC

# open tokenined titles

def jaccard_score_for_search(searchtext_tokenized, ditornary:dict)-> list[list[str, float]]:
    """
    Get the jaccard score between all mainTitle's and the search query from the user.
    """
    simularity_scores = []
    for index, tokens in ditornary.items():
        simularity = LC.jaccard_similarity(searchtext_tokenized, tokens)
        simularity_scores.append([index, simularity])        
    return simularity_scores


def tokenize(text:str)->list[str]:
    """
    Tokenize text
    """
    return text.lower().split(" ")

def get_search_result(df, searchtext:str, n_results=5)->pd.DataFrame:
    """
    Returns search results based on jaccard simularity. Searches among all mediaID
    """

    # might be usefull for debuggin if you know the mediaID
    if searchtext in df["mediaID"].unique():
        return df[df["mediaID"] == searchtext]
    
    with open('data/mediaID_MainTitleTokens.json') as json_file:
        tokenizedTitles = json.load(json_file)

    searchtext_tokenized = tokenize(searchtext)
    jaccard_scores_list = jaccard_score_for_search(searchtext_tokenized, tokenizedTitles)
    jaccard_scores_df = pd.DataFrame(jaccard_scores_list, columns=['mediaID','jaccard_score']).sort_values(by='jaccard_score', ascending=False)
    search_results = pd.merge(left=jaccard_scores_df, right=df, left_on='mediaID', right_on="mediaID", how="inner")
    return search_results.head(n_results)


def get_first_season(df, mainTitle:str)->pd.DataFrame:
    n_first_season = df[df["mainTitle"] == mainTitle]['season'].min()
    print(df[df['season'] == n_first_season]["mediaID"].sample(1).values[0])
    return df[df['season'] == n_first_season]["mediaID"].sample(1).values[0]   

def get_mediaID_from_first_season_random(df, jaccardscores:pd.DataFrame):
    mainTile2mediaID = []

    df_result = pd.DataFrame(columns=df.columns)
    jaccardscores["mediaID"] = jaccardscores['mainTile'].apply(lambda x: get_first_season(df, x))

    return jaccardscores.drop(columns=['mainTile'])


def get_search_result_v2(df, searchtext:str, n_results=5)-> pd.DataFrame:
    """
    Return search results based on jaccard simularty, returns unique mainTiles, only the first season/episode.
    """
    if searchtext in df["mediaID"].unique():
        return df[df["mediaID"] == searchtext]
    
    with open('data/mainTitle_mainTitleTokens.json') as json_file:
        tokenized_mainTitles = json.load(json_file)

    searchtext_tokenized = tokenize(searchtext)
    jaccard_scores = jaccard_score_for_search(searchtext_tokenized, tokenized_mainTitles)
    jaccard_scores_df = pd.DataFrame(jaccard_scores, columns=['mainTile','jaccard_score']).sort_values(by='jaccard_score', ascending=False)

    n_possible = min(n_results, len(jaccard_scores))
    mediaIDs = get_mediaID_from_first_season_random(df, jaccard_scores_df.head(n_possible))
    result = pd.merge(df, mediaIDs, how = 'inner').sort_values(by='jaccard_score', ascending=False)
    print(result)

    return result  # Placeholder in case it gets called

if __name__ == "__main__":
    df = pd.read_csv("data/NPOPlayerv2.csv")
    print(get_search_result_v2(df, 'op'))
