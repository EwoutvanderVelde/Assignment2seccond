import pandas as pd
import json
import numpy as np



# with open('activities.json', 'r') as fp:
#     activities = json.load(fp)

# print(activities)

# def get_all_user_ids():
#     user_list = set([activity["user_id"] for activity in activities])
#     return(user_list)

# print(get_all_user_ids())



df_activities = pd.read_json("activities.json")
df_npo = pd.read_csv("NPOPlayer.csv", sep=";")

df_selected = df_activities[df_activities['activity'] == "Select mediaID"]

userlist = list(df_selected["user_id"].unique())
mediaIDList = list(df_npo["mediaID"].unique())

userID_index = {}
index_userID = {}
for i, user in enumerate(userlist):
    userID_index[user] = i
    index_userID[i] = user

mediaID_index = {}
index_mediaID = {}
for i, mediaID in enumerate(mediaIDList):
    mediaID_index[mediaID] = i
    index_mediaID[i] = mediaID

rows = (len(userlist))
cols = (len(mediaIDList))
#large_empty=np.full((rows,cols),np.nan)
large_empty=np.zeros([rows,cols], dtype=np.int8)

# first itteration is over the rows, so the users!
for i, row in enumerate(large_empty):
    useractivities = df_selected[df_selected["user_id"] == index_userID[i]]
    for j in useractivities.iterrows():
        content_id = (j[1]["content_id"])
        columnindex = mediaID_index[content_id]
        row[columnindex] += 1
        print(i, columnindex)
#print(large_empty)

print(large_empty[7, 90635])

print(large_empty.nbytes)
 


# activities = (df_activities[df_activities['activity'] == "Select mediaID"])

