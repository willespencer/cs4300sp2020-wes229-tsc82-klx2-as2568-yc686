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

doc_id = 0

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

def genre_sim_score(query, podcast_dict, genre_query, genre_search):
    """ Returns the jaccard similarity of the genres of two podcasts

    query is a dictionary containing information about the query podcast
    """
    if genre_query != None:
        query_genres = set(query["genres"] + [genre_query])
    else:
        query_genres = set(query["genres"])
    podcast_genres = set(podcast_dict["genres"])
    score = len(query_genres & podcast_genres)/len(query_genres | podcast_genres)
    if genre_search and score < .5: 
        score += .5
    return score * 100


def jaccard_sim_score(query, podcast_dict, review_lst):
    """Returns an int percentage giving the jaccard similarity of 
    Step 1: Make a word blob of all the reviews and description of the query
    Step 2: Make a word blob of all the reviews and description of the podcast_dict
    Step 3: Do a jaccard sim of the two word blobs
    """
    word_blob_1 = set(make_word_blob(query, review_lst))
    word_blob_2 = set(make_word_blob(podcast_dict, review_lst))
    score = round(len(word_blob_1 & word_blob_2) * 100/len(word_blob_1 | word_blob_2))
    podcast_dict["similarities"] = [("Duration","TBD"), ("No. Episodes","TBD"), ("Genre","TBD"), ("Description",score)]
    podcast_dict["similarity"] = score
    return score

def description_cosine_sim_score(query, podcast_dict, inv_idx, idf, doc_norms, doc_id):
    # query is a dictionary representing the podcast that the user chose
    # podcast_dict is a dictionary that represents a podcast
    # review_lst is a list of dictionaries, and each dictionary represents a review of all podcasts in the database
    # query_word_lst = tokenize(query["description"])
    # podcast_word_lst = tokenize(podcast_dict["description"])

    # word_lst = enumerate(list(set(query_word_lst + podcast_word_lst)))
    # num_distinct_words = len(list(set(query_word_lst + podcast_word_lst)))
    # query_vec = np.zeros(num_distinct_words)
    # podcast_vec = np.zeros(num_distinct_words)

    # for (idx, each_word) in word_lst:
    #     query_vec[idx] = query_word_lst.count(each_word)
    #     podcast_vec[idx] = podcast_word_lst.count(each_word)

    # numerator = query_vec.dot(podcast_vec)
    # denominator = LA.norm(query_vec) * LA.norm(podcast_vec)
    # score = numerator / denominator
    # # podcast_dict["similarities"] = [("Duration", "TBD"), ("No. Episodes", "TBD"), ("Genre", "TBD"), ("Description", score), ("Reviews", "TBD")]
    # # podcast_dict["similarity"] = score
    # return score

    global doc_id
    query_words_lst = tokenizer.tokenize(query)
    query_words_set = list(set(query_words_lst))
    query_dict = {}

    numerator = 0
    denominator = 0

    for each_word in query_words_set:
        if each_word in inv_idx.keys():
            query_dict[each_word] = query_words_lst.count(each_word)

    for each_word in query_words_set:
        if each_word in idf:
            query_norm += (query_words_lst.count(each_word)*idf[each_word])**2

    query_norm = math.sqrt(query_norm)

    for each_token in query_dict:
        for each_doc in inv_idx[each_token]:
            numerator += (query_dict[each_token] * each_doc[1]) * (idf[each_token]**2)

    denominator = query_norm * doc_norm[doc_id]
    score = (numerator + 0.5) / (denominator + 0.5)
    doc_id += 1
    return score

def reviews_jaccard_sim_score(query, podcast_dict, review_lst, pod_name_to_idx_review_dict):
    """Returns the decimal form of the the jaccard similarity between query reviews
    and podcast reviews
    """
    query_word_lst = []
    for idx in pod_name_to_idx_review_dict[query["name"]]:
        review_text = review_lst[idx]["rev_text"]
        if review_text is not None:
            query_word_lst += tokenize(review_text)
    
    podcast_word_lst = []
    for idx in pod_name_to_idx_review_dict[podcast_dict["name"]]:
        review_text = review_lst[idx]["rev_text"]
        if review_text is not None:
            podcast_word_lst += tokenize(review_text)



    query_word_set = set(query_word_lst)
    podcast_word_set = set(podcast_word_lst)
    score = len(query_word_set & podcast_word_set)/len(query_word_set | podcast_word_set)
    return score





def reviews_cosine_sim_score(query, podcast_dict, review_lst, pod_name_to_idx_review_dict):
    # query is a dictionary representing the podcast that the user chose
    # podcast_dict is a dictionary that represents a podcast
    # review_lst is a list of dictionaries, and each dictionary represents a review of all podcasts in the database
    # pod_name_to_idx_review_dict is a dictionary that maps the pod_name for a review to the idx in review_lst
    

    ## AKIRA'S OPTIMIZATION
    # query_word_lst = []
    # for idx in pod_name_to_idx_review_dict[query["name"]]:
    #     review_text = review_lst[idx]["rev_text"]
    #     if review_text is not None:
    #         query_word_lst += tokenize(review_text)
    
    # podcast_word_lst = []
    # for idx in pod_name_to_idx_review_dict[podcast_dict["name"]]:
    #     review_text = review_lst[idx]["rev_text"]
    #     if review_text is not None:
    #         podcast_word_lst += tokenize(review_text)
    ## AKIRA'S OPTIMIZATION END

    query_word_lst = []
    query_review_lst = list(filter(lambda x: x["pod_name"] == query["name"], review_lst))
    for each_review in query_review_lst:
        if each_review["rev_text"] is None:
            query_word_lst += ''
        else:
            query_word_lst = query_word_lst + tokenize(each_review["rev_text"])
    
    podcast_word_lst = []
    podcast_review_lst = list(filter(lambda x: x["pod_name"] == podcast_dict["name"], review_lst))
    for each_review in podcast_review_lst:
        if each_review["rev_text"] is None:
            podcast_word_lst += ''
        else:
            podcast_word_lst = podcast_word_lst + tokenize(each_review["rev_text"])
    word_lst = enumerate(list(set(query_word_lst + podcast_word_lst)))
    num_distinct_words = len(list(set(query_word_lst + podcast_word_lst)))
    query_vec = np.zeros(num_distinct_words)
    podcast_vec = np.zeros(num_distinct_words)

    for (idx, each_word) in word_lst:
        query_vec[idx] = query_word_lst.count(each_word)
        podcast_vec[idx] = podcast_word_lst.count(each_word)
    

    numerator = query_vec.dot(podcast_vec) + 1
    denominator = LA.norm(query_vec) * LA.norm(podcast_vec) + 2
    score = numerator / denominator
    # podcast_dict["similarities"] = [("Duration", "TBD"), ("No. Episodes", "TBD"), ("Genre", "TBD"), ("Description", score), ("Reviews", "TBD")]
    # podcast_dict["similarity"] = score
    return score

def duration_sim_score(query, podcast_dict, is_adv_search):
    if is_adv_search:
        return 1
    elif query["avg_episode_duration"] == "None" or podcast_dict["avg_episode_duration"] == "None" or query["avg_episode_duration"] == 0 or podcast_dict["avg_episode_duration"] == 0:
        return 0
    else:
        query_duration = float(query["avg_episode_duration"])
        podcast_duration = float(podcast_dict["avg_episode_duration"])
        return max(0, 1 - (abs(query_duration - podcast_duration) / query_duration))

def num_ep_sim_score(query, podcast_dict, is_adv_search):
    if is_adv_search:
        return 1
    elif query["episode_count"] == "None" or podcast_dict["episode_count"] == "None" or query["episode_count"] == 0 or podcast_dict["episode_count"] == 0:
        return 0    
    else:
        query_count = float(query["episode_count"])
        podcast_count = float(podcast_dict["episode_count"])
        return max(0, 1 - (abs(query_count - podcast_count) / query_count))

def update_score(query, podcast_dict, review_lst, pod_name_to_idx_review_dict, genre_query, genre_search, avepdur_search, minepcount_search, inv_idx, idf, doc_norms):
    total_score = 0
    description_score = round((description_cosine_sim_score(query, podcast_dict, inv_idx, idf, doc_norms) * 100), 1)
    # review_score = round((reviews_cosine_sim_score(query, podcast_dict, review_lst, pod_name_to_idx_review_dict) * 100), 1)
    review_score = 0
    # review_score = round((reviews_jaccard_sim_score(query, podcast_dict, review_lst, pod_name_to_idx_review_dict) * 100) , 1)

    duration_score = round((duration_sim_score(query, podcast_dict, avepdur_search) * 100), 1)
    num_ep_score = round((num_ep_sim_score(query, podcast_dict, minepcount_search) * 100), 1)
    genre_score = round(genre_sim_score(query, podcast_dict, genre_query, genre_search), 1) # already 100%

    
    total_score = round(.45 * genre_score + .3 * description_score + .1*duration_score + .1*num_ep_score + .05*review_score)

    if np.isnan(total_score):
        total_score = -10000

    podcast_dict["similarities"] = [("Duration", str(duration_score)), ("No. Episodes", str(num_ep_score)), ("Genre", str(genre_score)), ("Description", str(description_score)), ("Reviews", str(review_score))]
    podcast_dict["similarity"] = str(total_score)
    return total_score


def get_ranked_podcast(query, podcast_lst, review_lst, pod_name_to_idx_review_dict, genre_query, inv_idx, idf, doc_norms, genre_search=False, avepdur_search=False, minepcount_search=False):
    # query is a dictionary representing the podcast that the user chose
    # podcast_lst is a list of dictionaries, and each dictionary represents a podcast
    # review_lst is a list of dictionaries, and each dictionary represents a review of all podcasts in the database
    # genre_query is the queried genre in advanced search. It is None if the user did not input one.
    # genre_search is a boolean that indicates whether a user is searching for a specific genre
    # avgepdur_search is a boolean that indicates whether a user is searching for a specific episode duration
    # minepcount_search is a boolean that indicates whether a user is searching for a specific minimum episode count
    
    # Returns a tuple of (score, podcast_data), so it will be an (int, dict) type
    # description_lst = list(map(lambda x: (x["description"], x), podcast_lst))
    global doc_id
    doc_id = 0
    score_lst = list(map(lambda x: (update_score(query, x, review_lst, pod_name_to_idx_review_dict, genre_query, genre_search, avepdur_search, minepcount_search, inv_idx, idf, doc_norms), x), podcast_lst))
    
    # KATHLEEN
    # score_lst = []

    # for podcast in podcast_lst:
    #     genre_score = genre_sim_score(query, podcast, genre_search)
    #     description_score = 0
    #     duration_score = 0
    #     epcount_score = 0
    #     review_score = 0
    #     podcast["similarities"] = [("Duration",duration_score), ("No. Episodes",epcount_score), ("Genre",genre_score), ("Description",description_score), ("Reviews", review_score)] 
    #     total_score = .35 * genre_score + .35 * description_score + .1*duration_score + .1*epcount_score + .1*review_score
    #     podcast["similarity"] = round(total_score)
    #     score_lst.append((total_score, podcast))
    # score_lst = list(map(lambda x: (jaccard_sim_score(query, x, review_lst), x), podcast_lst))
    sorted_lst = sorted(score_lst, key=lambda x: x[0], reverse=True)
    ranked_podcast_lst = list(map(lambda x: x[1], sorted_lst))
    return ranked_podcast_lst[:20]
