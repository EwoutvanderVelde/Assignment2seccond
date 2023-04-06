import pandas as pd
import json
import liveCalc as LC

DEBUG = False

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

# # DEPRECIATED
# def get_search_result(df, searchtext:str, n_results=5)->pd.DataFrame:
#     """
#     Returns search results based on jaccard simularity. Searches among all mediaID
#     """

#     # might be usefull for debuggin if you know the mediaID
#     if searchtext in df["mediaID"].unique():
#         return df[df["mediaID"] == searchtext]
    
#     with open('data/mediaID_MainTitleTokens.json') as json_file:
#         tokenizedTitles = json.load(json_file)

#     searchtext_tokenized = tokenize(searchtext)
#     jaccard_scores_list = jaccard_score_for_search(searchtext_tokenized, tokenizedTitles)
#     jaccard_scores_df = pd.DataFrame(jaccard_scores_list, columns=['mediaID','jaccard_score']).sort_values(by='jaccard_score', ascending=False)
#     search_results = pd.merge(left=jaccard_scores_df, right=df, left_on='mediaID', right_on="mediaID", how="inner")
#     return search_results.head(n_results)


def get_episode_from_first_season(df, mainTitle:str)->pd.DataFrame:
    """
    Returns a random episode from the first season of a mainTitle. 
    TODO Function could be improved by showing the fist episode, but we need the episode numbers for this.
    """
    show_episondes = df[df["mainTitle"] == mainTitle]
    n_first_season = show_episondes['season'].min()
    result = show_episondes[show_episondes['season'] == n_first_season]["mediaID"].sample(1).values[0]
    
    if DEBUG:
        print(f"searchReuslts.py get_first_season mainTitle \n{mainTitle}\n")
        print(f"searchReuslts.py get_first_season result \n{result}\n")
    
    return result  

def get_mediaID_from_first_season_random(df, jaccardscores:pd.DataFrame):
    """
    Funcion that swithces the mainTitle with a mediaID in jaccardscore dataframe
    """
    mainTile2mediaID = []
    jaccardscores["mediaID"] = jaccardscores['mainTile'].apply(lambda x: get_episode_from_first_season(df, x))
    
    if DEBUG:
        print(f"searchReuslts.py get_mediaID_from_fist_season_random jaccardscored_appended \n{jaccardscores}\n")
    
    return jaccardscores.drop(columns=['mainTile'])


def get_search_result_v2(df, searchtext:str, n_results=5)-> pd.DataFrame:
    """
    Return search results based on jaccard simularty.
    Output are build of a random episode from the frist season from unique mainTitles.
    TODO give first episode from first season, we need episode numbers for this. 

    """
    if searchtext in df["mediaID"].unique():
        return df[df["mediaID"] == searchtext]
    
    with open('data/mainTitle_mainTitleTokens.json') as json_file:
        tokenized_mainTitles = json.load(json_file)

    searchtext_tokenized = tokenize(searchtext)
    jaccard_scores = jaccard_score_for_search(searchtext_tokenized, tokenized_mainTitles)
    jaccard_scores_df = pd.DataFrame(jaccard_scores, columns=['mainTile','jaccard_score']).sort_values(by='jaccard_score', ascending=False)
    
    n_possible = min(n_results, len(jaccard_scores))
    mediaIDs = get_mediaID_from_first_season_random(df, jaccard_scores_df.head(n_possible).copy())
    result = pd.merge(df, mediaIDs, how = 'inner').sort_values(by='jaccard_score', ascending=False)
    
    if DEBUG:
        print(f"searchResult.py get_search_resutls_v2 jaccard_scores_df: \n{jaccard_scores_df}\n")
        print(f"searchResult.py get_search_resutls_v2 result: \n{result}\n")

    return result  # Placeholder in case it gets called


# Will
if __name__ == "__main__":
    DEBUG = True
    df = pd.read_csv("data/NPOPlayerv2.csv")
    print(get_search_result_v2(df, 'op'))
