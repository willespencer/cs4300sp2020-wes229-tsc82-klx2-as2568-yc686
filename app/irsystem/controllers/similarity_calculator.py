import re
import json
from glob import glob
import os
from io import StringIO
from itertools import groupby
import pickle
import math
import numpy as np
from numpy import linalg as LA


from app.irsystem.controllers.query_db import *
# from app.irsystem.controllers.inv_idx import *
# from app.irsystem.controllers.idf import *
# from app.irsystem.controllers.doc_norms import *

# from inv_idx import inv_idx
# from idf import idf
# from doc_norms import doc_norms
# import time


project_name = "Find the Pea to your Podcast"
net_id = "Will Spencer: wes229, Theresa Cho: tsc82, Kathleen Xu: klx2, Yvonne Chan: yc686, Akira Shindo: as2568"

# doc_id = 0


def tokenize(text):
    """Returns a list of words that make up the text.

    Note: for simplicity, lowercase everything.
    Requirement: Use Regex to satisfy this function

    Params: {text: String}
    Returns: List
    """
    # YOUR CODE HERE
    return re.findall("[A-Za-z]+", text.lower())


def make_word_blob(podcast_dict):
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
    score = len(query_genres & podcast_genres) / \
        len(query_genres | podcast_genres)
    if genre_search and score < .5:
        score += .5
    return score * 100


def jaccard_sim_score(query, podcast_dict):
    """Returns an int percentage giving the jaccard similarity of 
    Step 1: Make a word blob of all the reviews and description of the query
    Step 2: Make a word blob of all the reviews and description of the podcast_dict
    Step 3: Do a jaccard sim of the two word blobs
    """
    word_blob_1 = set(make_word_blob(query))
    word_blob_2 = set(make_word_blob(podcast_dict))
    score = round(len(word_blob_1 & word_blob_2) *
                  100/len(word_blob_1 | word_blob_2))
    podcast_dict["similarities"] = [
        ("Duration", "TBD"), ("No. Episodes", "TBD"), ("Genre", "TBD"), ("Description", score)]
    podcast_dict["similarity"] = score
    return score


def description_cosine_sim_score(query, podcast_dict, inv_idx, idf, doc_norms):
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

    query_words_lst = tokenize(query["description"])
    query_words_set = list(set(query_words_lst))
    query_dict = {}
    query_norm = 0
    doc_pos_lst = []
    search_results = []
    search_results_dict = {}
    # search_results_dict is a dictionary with the doc_id as key and score as value

    numerator = 0
    denominator = 0

    # SECTION 1
    # start_time = time.time()
    for each_word in query_words_set:
        if each_word in inv_idx.keys():
            query_dict[each_word] = query_words_lst.count(each_word)
    # print("Section 1 time: ")
    # print (time.time() - start_time)

    # SECTION 2
    # start_time = time.time()
    for each_word in query_words_set:
        if each_word in idf:
            query_norm += (query_words_lst.count(each_word)*idf[each_word])**2
    query_norm = math.sqrt(query_norm)
    # print("Section 2 time: ")
    # print (time.time() - start_time)
    # SECTION 3
    # start_time = time.time()
    # print(query_dict)

    # for each_token in query_dict:
    #     if len(inv_idx[each_token]) <= 1000:
    #         for each_doc in inv_idx[each_token]:
    #             if each_token in idf.keys():
    #                 numerator = (query_dict[each_token]
    #                              * each_doc[1]) * (idf[each_token]**2)
    #                 if each_doc[0] not in doc_pos_lst:
    #                     search_results.append([numerator, each_doc[0]])
    #                     doc_pos_lst.append(each_doc[0])
    #                 else:
    #                     search_results[doc_pos_lst.index(
    #                         each_doc[0])][0] += numerator




    for each_token in query_dict:
        for each_doc in inv_idx[each_token]:
            numerator = (query_dict[each_token] * each_doc[1]) * (idf[each_token]**2)
            if each_doc[0] not in doc_pos_lst:
                search_results.append([numerator, each_doc[0]])
                doc_pos_lst.append(each_doc[0])
            else:
                search_results[doc_pos_lst.index(each_doc[0])][0] += numerator

    for x in range(len(doc_pos_lst)):
        denominator = query_norm * doc_norms[doc_pos_lst[x]]
        results = search_results[x]
        search_results_dict[results[1]] = (results[0] / denominator)
    return search_results_dict

    # print("Section 3 time: ")
    # print(time.time() - start_time)
    # print()

    # print(type(query_norm))
    # print(type(doc_norms[doc_id]))
    # denominator = query_norm * doc_norms[doc_id]
    # score = (numerator + 0.5) / (denominator + 0.5)
    # doc_id += 1

    # print(score)

    # if score > 1000:
    #     score = 0
    # elif score > 100:
    #     score = 100

    # return score


def reviews_jaccard_sim_score(query, podcast_dict):
    """Returns the decimal form of the the jaccard similarity between query reviews
    and podcast reviews
    """
    query_word_lst = []
    query_reviews = [query["review1"], query["review2"],
                     query["review3"], query["review4"], query["review5"]]
    for review_text in query_reviews:
        if review_text is not None:
            query_word_lst += tokenize(review_text)

    podcast_word_lst = []
    podcast_reviews = [podcast_dict["review1"], podcast_dict["review2"],
                       podcast_dict["review3"], podcast_dict["review4"], podcast_dict["review5"]]
    for review_text in podcast_reviews:
        if review_text is not None:
            podcast_word_lst += tokenize(review_text)

    query_word_set = set(query_word_lst)
    podcast_word_set = set(podcast_word_lst)
    if len(query_word_set | podcast_word_set) != 0:
        score = len(query_word_set & podcast_word_set) / len(query_word_set | podcast_word_set)
    else:
        score = 0
    return score

# deprecated


def reviews_cosine_sim_score(query, podcast_dict, review_lst):
    # query is a dictionary representing the podcast that the user chose
    # podcast_dict is a dictionary that represents a podcast
    # review_lst is a list of dictionaries, and each dictionary represents a review of all podcasts in the database
    # pod_name_to_idx_review_dict is a dictionary that maps the pod_name for a review to the idx in review_lst

    # AKIRA'S OPTIMIZATION
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
    # AKIRA'S OPTIMIZATION END

    query_word_lst = []
    query_review_lst = list(
        filter(lambda x: x["pod_name"] == query["name"], review_lst))
    for each_review in query_review_lst:
        if each_review["rev_text"] is None:
            query_word_lst += ''
        else:
            query_word_lst = query_word_lst + tokenize(each_review["rev_text"])

    podcast_word_lst = []
    podcast_review_lst = list(
        filter(lambda x: x["pod_name"] == podcast_dict["name"], review_lst))
    for each_review in podcast_review_lst:
        if each_review["rev_text"] is None:
            podcast_word_lst += ''
        else:
            podcast_word_lst = podcast_word_lst + \
                tokenize(each_review["rev_text"])
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


# def update_score(query, podcast_dict, review_lst, genre_query, genre_search, avepdur_search, minepcount_search, inv_idx, idf, doc_norms):
#     total_score = 0
#     # start_time = time.time()
#     description_score = round((description_cosine_sim_score(
#         query, podcast_dict, inv_idx, idf, doc_norms)), 1)
#     # print("Description time: ")
#     # print (time.time() - start_time)
#     # review_score = round((reviews_cosine_sim_score(query, podcast_dict) * 100), 1)
#     review_score = 0
#     # review_score = round((reviews_jaccard_sim_score(
#     #     query, podcast_dict) * 100), 1)

#     # start_time = time.time()
#     duration_score = round(
#         (duration_sim_score(query, podcast_dict, avepdur_search) * 100), 1)
#     # print("Duration time: ")
#     # print (time.time() - start_time)

#     # start_time = time.time()
#     num_ep_score = round(
#         (num_ep_sim_score(query, podcast_dict, minepcount_search) * 100), 1)
#     # print("Number of eipsode time: ")
#     # print (time.time() - start_time)

#     # start_time = time.time()
#     genre_score = round(genre_sim_score(query, podcast_dict,
#                                         genre_query, genre_search), 1)  # already 100%
#     # print("Genre time: ")
#     # print (time.time() - start_time)
#     # print()

#     total_score = round(.45 * genre_score + .3 * description_score + .1 *
#                         duration_score + .1*num_ep_score + .05*review_score)

#     if np.isnan(total_score):
#         total_score = -10000

#     podcast_dict["similarities"] = [("Duration", str(duration_score)), ("No. Episodes", str(num_ep_score)), ("Genre", str(
#         genre_score)), ("Description", str(description_score)), ("Reviews", str(review_score))]
#     podcast_dict["similarity"] = str(total_score)
#     return total_score


def get_ranked_podcast(query, podcast_lst, genre_query, inv_idx, idf, doc_norms, genre_search=False, avepdur_search=False, minepcount_search=False):
    # query is a dictionary representing the podcast that the user chose
    # podcast_lst is a list of dictionaries, and each dictionary represents a podcast
    # genre_query is the queried genre in advanced search. It is None if the user did not input one.
    # genre_search is a boolean that indicates whether a user is searching for a specific genre
    # avgepdur_search is a boolean that indicates whether a user is searching for a specific episode duration
    # minepcount_search is a boolean that indicates whether a user is searching for a specific minimum episode count

    # Returns a tuple of (score, podcast_data), so it will be an (int, dict) type
    # description_lst = list(map(lambda x: (x["description"], x), podcast_lst))

    # description_score_lst is like [(score, 0), (score, 1) ... (score, doc_id)...]

    score_lst = []
    description_score_dict = description_cosine_sim_score(
        query, {}, inv_idx, idf, doc_norms)

    for i in range(len(podcast_lst)):
        podcast_dict = podcast_lst[i]
        total_score = 0
        # start_time = time.time()
        if i in description_score_dict:
            description_score = round(description_score_dict[i] * 100, 1)
        else:
            description_score = 76.5
        # print("Description time: ")
        description_score = round(jaccard_sim_score(query, podcast_dict))
        # print (time.time() - start_time)
        # review_score = round((reviews_cosine_sim_score(query, podcast_dict) * 100), 1)
        # review_score = 0
        review_score = round(
            (reviews_jaccard_sim_score(query, podcast_dict) * 100), 1)

        # start_time = time.time()
        duration_score = round(
            (duration_sim_score(query, podcast_dict, avepdur_search) * 100), 1)
        # print("Duration time: ")
        # print (time.time() - start_time)

        # start_time = time.time()
        num_ep_score = round(
            (num_ep_sim_score(query, podcast_dict, minepcount_search) * 100), 1)
        # print("Number of eipsode time: ")
        # print (time.time() - start_time)

        # start_time = time.time()
        genre_score = round(genre_sim_score(
            query, podcast_dict, genre_query, genre_search), 1)  # already 100%
        # print("Genre time: ")
        # print (time.time() - start_time)
        # print()

        total_score = round(.45 * genre_score + .3 * description_score + .1 *
                            duration_score + .1*num_ep_score + .05*review_score)

        if np.isnan(total_score):
            total_score = -10000

        podcast_dict["similarities"] = [("Duration", str(duration_score)), ("No. Episodes", str(num_ep_score)), ("Genre", str(
            genre_score)), ("Description", str(description_score)), ("Reviews", str(review_score))]
        podcast_dict["similarity"] = str(total_score)
        score_lst += [(total_score, podcast_lst[i])]

    sorted_lst = sorted(score_lst, key=lambda x: x[0], reverse=True)
    ranked_podcast_lst = list(map(lambda x: x[1], sorted_lst))
    return ranked_podcast_lst[:20]

    # score_lst = list(map(lambda x: (update_score(query, x, review_lst, genre_query,
    #                                              genre_search, avepdur_search, minepcount_search, inv_idx, idf, doc_norms), x), podcast_lst))

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


# def main():
#     global inv_idx
#     global idf
#     global doc_norms
#     print("The following is the score...")
#     print("The query description is: Hello this is a and and test radio radio")
#     for each_elem in get_ranked_podcast(
#         {"name": 'query', "description": "Hello this is a and and our test radio radio",
#             "episode_count": "5", "avg_episode_duration": "10", "genres": ["Literature"]},
#         [{"name": 'pod_1', "description": "Hello hello this a test is", "episode_count": "6", "avg_episode_duration": "None", "genres": ["Literature"]},
#          {"name": 'pod_2', "description": "Hello a test.", "episode_count": "4",
#              "avg_episode_duration": "9", "genres": ["Literature"]},
#          {"name": 'pod_3', "description": "Hello a", "episode_count": "8", "avg_episode_duration": "500", "genres": ["Literature"]}],
#         [{'pod_name': 'query', 'rev_text': "podcast sucks"},
#          {'pod_name': 'pod_1', 'rev_text': "this podcast sucks"},
#          {'pod_name': 'pod_2', 'rev_text': "this podcast is great"},
#          {'pod_name': 'pod_3', 'rev_text': "this podcast is ok I guess"}],
#         inv_idx,
#         idf,
#             doc_norms):
#         print(each_elem)

# main()
