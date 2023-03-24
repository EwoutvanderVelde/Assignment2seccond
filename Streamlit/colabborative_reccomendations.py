import pandas as pd
import json

df = pd.read_json("activities.json")

def get_all_users():
    return (list(df["user_id"].unique()))

def get_user_activities(user_id):
    return df[df["user_id"] == user_id]


