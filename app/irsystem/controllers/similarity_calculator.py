import re
import json
from glob import glob
import os
from io import StringIO
from itertools import groupby
import pickle

import numpy as np
from numpy import linalg as LA

project_name = "Find the Pea to your Podcast"
net_id = "Will Spencer: wes229, Theresa Cho: tsc82, Kathleen Xu: klx2, Yvonne Chan: yc686, Akira Shindo: as2568"

def tokenize(text):
    """Returns a list of words that make up the text.
    
    Note: for simplicity, lowercase everything.
    Requirement: Use Regex to satisfy this function
    
    Params: {text: String}
    Returns: List
    """
    # YOUR CODE HERE
    return re.findall("[A-Za-z]+", text.lower())

def bool_and_sim_score(query, podcast_dict):
    """Returns a float giving the boolean and similarity of 
    """
    # YOUR CODE HERE
    query_set = set(tokenize(query))
    podcast_description_set = set(tokenize(podcast_dict["description"]))
    score = len(query_set & podcast_description_set)
    podcast_dict["similarities"] = [("Duration", "TBD"), ("No. Episodes", "TBD"), ("Genre", "TBD"), ("Description", score)]
    podcast_dict["similarity"] = score
    return score

def get_ranked_podcast(query, podcast_lst):
    # podcast_title_lst is a list of dictionaries, and each dictionary represents a podcast
    # Returns a tuple of (score, podcast_data), so it will be an (int, dict) type
    # description_lst = list(map(lambda x: (x["description"], x), podcast_lst))
    score_lst = list(map(lambda x: (bool_and_sim_score(query, x), x), podcast_lst))
    sorted_lst = sorted(score_lst, key=lambda x: x[0], reverse=True)
    ranked_podcast_lst = list(map(lambda x: x[1], sorted_lst))
    return ranked_podcast_lst[:20]

def main():
    print("The following is the score...")
    print(get_ranked_podcast("Hello this is a test", [{"description": "Hello", "similarities": []}, {"description": "Hello a test.", "similarities": []}, {"description": "Hello a", "similarities": []}]))

main()
# def get_top_rankings(query, )
