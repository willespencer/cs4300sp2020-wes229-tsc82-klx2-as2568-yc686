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

def make_word_blob(podcast_dict, review_lst):
    word_blob = []
    word_blob = word_blob + tokenize(podcast_dict["description"])
    # relevant_review_lst = list(filter(lambda x: x["pod_name"] == podcast_dict["name"], review_lst))
    # for each_review in relevant_review_lst:
    #     word_blob = word_blob + tokenize(each_review["rev_text"])
    return word_blob


def jaccard_sim_score(query, podcast_dict, review_lst):
    """Returns an int percentage giving the jaccard similarity of 
    Step 1: Make a word blob of all the reviews and description of the query
    Step 2: Make a word blob of all the reviews and description of the podcast_dict
    Step 3: Do a jaccard sim of the two word blobs
    """
    # YOUR CODE HERE
    word_blob_1 = set(make_word_blob(query, review_lst))
    word_blob_2 = set(make_word_blob(podcast_dict, review_lst))
    score = round(len(word_blob_1 & word_blob_2) * 100/len(word_blob_1 | word_blob_2))
    podcast_dict["similarities"] = [("Duration", "TBD"), ("No. Episodes", "TBD"), ("Genre", "TBD"), ("Description", score)]
    podcast_dict["similarity"] = score
    return score

def description_cosine_sim_score(query, podcast_dict):
    # query is a dictionary representing the podcast that the user chose
    # podcast_dict is a dictionary that represents a podcast
    # review_lst is a list of dictionaries, and each dictionary represents a review of all podcasts in the database
    query_word_lst = tokenize(query["description"])
    podcast_word_lst = tokenize(podcast_dict["description"])

    word_lst = enumerate(list(set(query_word_lst + podcast_word_lst)))
    num_distinct_words = len(list(set(query_word_lst + podcast_word_lst)))
    query_vec = np.zeros(num_distinct_words)
    podcast_vec = np.zeros(num_distinct_words)

    for (idx, each_word) in word_lst:
        query_vec[idx] = query_word_lst.count(each_word)
        podcast_vec[idx] = podcast_word_lst.count(each_word)

    numerator = query_vec.dot(podcast_vec)
    denominator = LA.norm(query_vec) * LA.norm(podcast_vec)
    score = numerator / denominator
    # podcast_dict["similarities"] = [("Duration", "TBD"), ("No. Episodes", "TBD"), ("Genre", "TBD"), ("Description", score), ("Reviews", "TBD")]
    # podcast_dict["similarity"] = score
    return score

def reviews_cosine_sim_score(query, podcast_dict, review_lst):
    # query is a dictionary representing the podcast that the user chose
    # podcast_dict is a dictionary that represents a podcast
    # review_lst is a list of dictionaries, and each dictionary represents a review of all podcasts in the database
    query_word_lst = []
    query_review_lst = list(filter(lambda x: x["pod_name"] == query["name"], review_lst))
    for each_review in query_review_lst:
        query_word_lst = query_word_lst + tokenize(each_review["rev_text"])

    podcast_word_lst = []
    podcast_review_lst = list(filter(lambda x: x["pod_name"] == podcast_dict["name"], review_lst))
    for each_review in podcast_review_lst:
        podcast_word_lst = podcast_word_lst + tokenize(each_review["rev_text"])

    word_lst = enumerate(list(set(query_word_lst + podcast_word_lst)))
    num_distinct_words = len(list(set(query_word_lst + podcast_word_lst)))
    query_vec = np.zeros(num_distinct_words)
    podcast_vec = np.zeros(num_distinct_words)

    for (idx, each_word) in word_lst:
        query_vec[idx] = query_word_lst.count(each_word)
        podcast_vec[idx] = podcast_word_lst.count(each_word)

    numerator = query_vec.dot(podcast_vec)
    denominator = LA.norm(query_vec) * LA.norm(podcast_vec)
    score = numerator / denominator
    # podcast_dict["similarities"] = [("Duration", "TBD"), ("No. Episodes", "TBD"), ("Genre", "TBD"), ("Description", score), ("Reviews", "TBD")]
    # podcast_dict["similarity"] = score
    return score

def duration_sim_score(query, podcast_dict, is_adv_search):
    if is_adv_search:
        return 1
    else:
        query_duration = query["avg_episode_duration"]
        podcast_duration = podcast_dict["avg_episode_duration"]
        return 1 - (abs(query_duration - podcast_duration) / query_duration)

def num_ep_sim_score(query, podcast_dict, is_adv_search):
    if is_adv_search:
        return 1
    else:
        query_count = query["episode_count"]
        podcast_count = podcast_dict["episode_count"]
        return 1 - (abs(query_count - podcast_count) / query_count)

def update_score(query, podcast_dict, review_lst, genre_search, avepdur_search, minepcount_search):
    total_score = 0
    description_score = description_cosine_sim_score(query, podcast_dict)
    review_score = reviews_cosine_sim_score(query, podcast_dict, review_lst)
    duration_score = duration_sim_score(query, podcast_dict, avepdur_search)
    num_ep_score = num_ep_sim_score(query, podcast_dict, minepcount_search)

    total_score = description_score + review_score + duration_score + num_ep_score
    podcast_dict["similarities"] = [("Duration", duration_score), ("No. Episodes", num_ep_score), ("Genre", "TBD"), ("Description", description_score), ("Reviews", review_score)]
    podcast_dict["similarity"] = total_score
    return total_score


def get_ranked_podcast(query, podcast_lst, review_lst, genre_search=False, avepdur_search=False, minepcount_search=False):
    # query is a dictionary representing the podcast that the user chose
    # podcast_lst is a list of dictionaries, and each dictionary represents a podcast
    # review_lst is a list of dictionaries, and each dictionary represents a review of all podcasts in the database
    # Returns a tuple of (score, podcast_data), so it will be an (int, dict) type
    # description_lst = list(map(lambda x: (x["description"], x), podcast_lst))
    score_lst = list(map(lambda x: (update_score(query, x, review_lst, genre_search, avepdur_search, minepcount_search), x), podcast_lst))
    sorted_lst = sorted(score_lst, key=lambda x: x[0], reverse=True)
    ranked_podcast_lst = list(map(lambda x: x[1], sorted_lst))
    return ranked_podcast_lst[:20]

def main():
    print("The following is the score...")
    print("The query description is: Hello this is a test")
    for each_elem in get_ranked_podcast(
        {"name": 'query', "description": "Hello this is a test", "episode_count": 5, "avg_episode_duration": 10}, 
        [{"name": 'pod_1', "description": "Hello hello this a test is", "episode_count": 6, "avg_episode_duration": 11}, 
        {"name": 'pod_2', "description": "Hello a test.", "episode_count": 4, "avg_episode_duration": 9}, 
        {"name": 'pod_3', "description": "Hello a", "episode_count": 8, "avg_episode_duration": 5}],
        [{'pod_name': 'query', 'rev_text': "podcast sucks"}, 
        {'pod_name': 'pod_1', 'rev_text': "this podcast sucks"}, 
        {'pod_name': 'pod_2', 'rev_text': "this podcast is great"}, 
        {'pod_name': 'pod_3', 'rev_text': "this podcast is ok I guess"}]):
        print(each_elem)

main()
# def get_top_rankings(query, )
