from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from app.irsystem.models.podcasts import Podcasts
from app.irsystem.controllers.similarity_calculator import *
from app.irsystem.controllers.query_db import *
from app.irsystem.controllers.inv_idx import *
from app.irsystem.controllers.idf import *
from app.irsystem.controllers.doc_norms import *

import json
import csv

project_name = "Find the Pea to your Podcast"
net_id = "Will Spencer: wes229, Theresa Cho: tsc82, Kathleen Xu: klx2, Yvonne Chan: yc686, Akira Shindo: as2568"


def cleanGenreQuery(genre_query):
    if genre_query:
        return genre_query
    else:
        return None


def cleanAvgEpDurationQuery(avg_ep_duration_query):
    if avg_ep_duration_query and avg_ep_duration_query.find('+') == -1:
        max_ep_duration_query = int(avg_ep_duration_query[avg_ep_duration_query.index(
            "-")+1:avg_ep_duration_query.index(" ")])
        min_ep_duration_query = int(
            avg_ep_duration_query[:avg_ep_duration_query.index("-")])
    elif avg_ep_duration_query:
        max_ep_duration_query = float('inf')
        min_ep_duration_query = int(
            avg_ep_duration_query[:avg_ep_duration_query.find("+")])
    else:
        max_ep_duration_query = None
        min_ep_duration_query = 0

    return (max_ep_duration_query, min_ep_duration_query)


def cleanMinEpCountQuery(min_ep_count_query):
    if min_ep_count_query:
        return int(min_ep_count_query[:min_ep_count_query.index(" ")])
    else:
        return 0


def build_inverted_index(podcast_lst):
    """ Builds an inverted index from the messages.

    Arguments
    =========

    podcast_lst: list of dicts.
        Each message in this list already has a 'toks'
        field that contains the tokenized message.

    Returns
    =======

    inverted_index: dict
        For each term, the index contains 
        a sorted list of tuples (doc_id, count_of_term_in_doc)
        such that tuples with smaller doc_ids appear first:
        inverted_index[term] = [(d1, tf1), (d2, tf2), ...]

    Example
    =======

    >> test_idx = build_inverted_index([
    ...    {'toks': ['to', 'be', 'or', 'not', 'to', 'be']},
    ...    {'toks': ['do', 'be', 'do', 'be', 'do']}])

    >> test_idx['be']
    [(0, 2), (1, 2)]

    >> test_idx['not']
    [(0, 1)]

    """
    doc_id = 0
    word_set = {}
    inverted_index = {}
    for each_dict in podcast_lst:
        word_set = set(tokenize(each_dict["description"]))
        for each_word in word_set:
            if each_word in inverted_index.keys():
                inverted_index[each_word] += [
                    (doc_id, tokenize(each_dict["description"]).count(each_word))]
            else:
                inverted_index[each_word] = [
                    (doc_id, tokenize(each_dict["description"]).count(each_word))]
        word_set.clear()
        doc_id += 1

    return inverted_index


def compute_idf(inv_idx, n_docs, min_df=10, max_df_ratio=0.95):
    """ Compute term IDF values from the inverted index.
    Words that are too frequent or too infrequent get pruned.

    Hint: Make sure to use log base 2.

    Arguments
    =========

    inv_idx: an inverted index as above

    n_docs: int,
        The number of documents.

    min_df: int,
        Minimum number of documents a term must occur in.
        Less frequent words get ignored. 
        Documents that appear min_df number of times should be included.

    max_df_ratio: float,
        Maximum ratio of documents a term can occur in.
        More frequent words get ignored.

    Returns
    =======

    idf: dict
        For each term, the dict contains the idf value.

    """

    # YOUR CODE HERE
    idf = {}
    for word, lst in inv_idx.items():
        if min_df <= len(lst) and len(lst) <= (max_df_ratio * n_docs):
            idf[word] = math.log2(n_docs / (1 + len(lst)))
    return idf


def compute_doc_norms(index, idf, n_docs):
    """ Precompute the euclidean norm of each document.

    Arguments
    =========

    index: the inverted index as above

    idf: dict,
        Precomputed idf values for the terms.

    n_docs: int,
        The total number of documents.

    Returns
    =======

    norms: np.array, size: n_docs
        norms[i] = the norm of document i.
    """
    summation = np.zeros(n_docs)
    for key, lst in index.items():
        for (doc_id, count) in lst:
            try:
                summation[doc_id] += (count*idf[key])**2
            except KeyError:
                pass
    norm_lst = np.array(list(map(lambda x: math.sqrt(x), list(summation))))
    return norm_lst


@irsystem.route('/', methods=['GET'])
def search():
    # uncleaned user input
    query_uncleaned = request.args.get('podcast_search')
    genre_query_uncleaned = request.args.get('genre_search')
    avg_ep_duration_query_uncleaned = request.args.get('avg_ep_duration')
    min_ep_count_query_uncleaned = request.args.get('min_ep_count')

    # user inputs and cleaning.
    # Handles case if genre, avg_ep_duration, min_ep_count not inputted
    query = query_uncleaned
    genre_query = cleanGenreQuery(genre_query_uncleaned)
    # avg_ep_duration_query is tuple (<max>, <min>)
    avg_ep_duration_query = cleanAvgEpDurationQuery(
        avg_ep_duration_query_uncleaned)
    min_ep_count_query = cleanMinEpCountQuery(min_ep_count_query_uncleaned)

    # advancedQuery dict tracks whether advancedQuery fields are filled
    # advancedQueryDict["genre"] = True if genre has been inputted
    advancedQueryDict = {
        "genre": genre_query != None,
        "avg_ep_duration": avg_ep_duration_query[0] != None and avg_ep_duration_query[1] != 0,
        "min_ep_count": min_ep_count_query != 0
    }

    # TODO: comment out to see breaking change for advancedPodcastData
    advancedQueryIsEnabled = advancedQueryDict["genre"] or advancedQueryDict[
        "avg_ep_duration"] or advancedQueryDict["min_ep_count"]

    # Note: the order changes everytime it's queried for some reason
    podcast_names = getAllPodcastNames()
    genres = getAllGenres()

    avg_ep_durations = ["0-25 min", "25-50 min", "50-75 min", "75+ min"]
    min_ep_counts = ["5 episodes", "10 episodes",
                     "50 episodes", "100 episodes"]

    max_ep_dur = db.session.query(db.func.max(Podcasts.ep_durations)).scalar()
    min_ep_dur = db.session.query(
        db.func.min(Podcasts.ep_durations)).scalar()
    max_ep_count = db.session.query(db.func.max(Podcasts.ep_count)).scalar()
    min_ep_count = db.session.query(
        db.func.min(Podcasts.ep_count)).scalar()

    if not query:
        data_dict_list = []
    else:
        if advancedQueryIsEnabled:
            podcast_lst = advancedPodcastData(
                genre_query, min_ep_count_query, avg_ep_duration_query[0], avg_ep_duration_query[1])
        else:
            podcast_lst = getPodcastData()

        # TODO: pass reviews with each podcast so only query once
        # TODO: sort podcast data so it's in specific order every time
        # TODO: recompute idf, inv_idx, doc_norms based on new order

        # if advancedQuery enabled
        # advancedQuery = advancedPodcastData(
        #     "Literature", 10, 10, 5)
        # print(advancedQuery)
        # print(len(advancedQuery))

        # calculates similarity scores

        # accum a list of all reviews for every podcast in podcast_lst and the query podcast
        # initially gets all podcast reviews

        review_lst = getPodcastReviews()

        podcast_lst_names = [query] + [podcast["name"]
                                       for podcast in podcast_lst]

        review_lst = list(
            filter(lambda x: x["pod_name"] in podcast_lst_names, review_lst))

        # pod_name_to_idx_review_dict = {}
        # for (idx, review) in enumerate(review_lst):
        #     try:
        #         pod_name_to_idx_review_dict[review["pod_name"]
        #                                     ] = pod_name_to_idx_review_dict[review["pod_name"]] + [idx]
        #     except KeyError:
        #         pod_name_to_idx_review_dict[review["pod_name"]] = [idx]
        # print(pod_name_to_idx_review_dict[query])
        # print(getPodcastReviews(query))

        # inv_idx = {}
        # with open('data/inv_idx.csv', mode='r') as infile:
        #     reader = csv.reader(infile)
        #     for rows in reader:
        #         term_info = rows[1].replace('\"', '').replace(
        #             '[', '').replace(']', '').split("), (")
        #         for x in range(len(term_info)):
        #             doc_info = term_info[x].replace(
        #                 '(', '').replace(')', '').split(", ")
        #             term_info[x] = (int(doc_info[0]), int(doc_info[1]))
        #         inv_idx[rows[0]] = term_info
        # # print(inv_idx)

        # idf = {}
        # with open('data/idf.csv', mode='r') as infile:
        #     reader = csv.reader(infile)
        #     idf = {rows[0]: float(rows[1]) for rows in reader}

        # f = open('data/doc_norms.txt', 'r')
        # doc_norms = f.readlines()
        # f.close()
        # doc_norms = doc_norms[0]
        # doc_norms = doc_norms.replace('[', '').replace(']', '').split(", ")
        # doc_norms = [float(i) for i in doc_norms]
        # # print(doc_norms)

        # createDocFiles = False

        # if createDocFiles:
        #     # write output to seperate file so we can just pull from that for our data
        #     w = csv.writer(open("data/inv_idx.csv", "w"))
        #     for key, val in inv_idx.items():
        #         w.writerow([key, val])

        #     h = csv.writer(open("data/idf.csv", "w"))
        #     for key, val in idf.items():
        #         h.writerow([key, val])

        #     f = open("data/doc_norms.txt", "w")
        #     f.write(str(doc_norms.tolist()))
        #     f.close()

        global inv_idx
        global idf
        global doc_norms

        if advancedQueryIsEnabled:
            inv_idx = build_inverted_index(podcast_lst)  # dict
            idf = compute_idf(inv_idx, len(podcast_lst))  # dict
            doc_norms = compute_doc_norms(
                inv_idx, idf, len(podcast_lst))  # list
        # else:
        #     inv_idx = {}
        #     with open('data/inv_idx.csv', mode='r') as infile:
        #         reader = csv.reader(infile)
        #         for rows in reader:
        #             term_info = rows[1].replace('\"', '').replace(
        #                 '[', '').replace(']', '').split("), (")
        #             for x in range(len(term_info)):
        #                 doc_info = term_info[x].replace(
        #                     '(', '').replace(')', '').split(", ")
        #                 term_info[x] = (int(doc_info[0]), int(doc_info[1]))
        #             inv_idx[rows[0]] = term_info
        #     # print(inv_idx)

        #     idf = {}
        #     with open('data/idf.csv', mode='r') as infile:
        #         reader = csv.reader(infile)
        #         idf = {rows[0]: float(rows[1]) for rows in reader}

        #     f = open('data/doc_norms.txt', 'r')
        #     doc_norms = f.readlines()
        #     f.close()
        #     doc_norms = doc_norms[0]
        #     doc_norms = doc_norms.replace('[', '').replace(']', '').split(", ")
        #     doc_norms = [float(i) for i in doc_norms]
            # print(doc_norms)

        data_dict_list = get_ranked_podcast(getPodcastData(
            query)[0], podcast_lst, review_lst,
            genre_query,
            inv_idx,
            idf,
            doc_norms,
            advancedQueryDict["genre"],
            advancedQueryDict["avg_ep_duration"],
            advancedQueryDict["min_ep_count"])
        # print(data_dict_list)

    # remove querried podcast from showing in result list, and round avg durration and episode count
    index_of_podcast = 0
    found_query = False
    for i in range(len(data_dict_list)):

        data_dict_list[i]['reviews'] = list(
            filter(lambda x: x["pod_name"] == data_dict_list[i]['name'], review_lst))
        if(data_dict_list[i]['name'] == query):
            index_of_podcast = i
            found_query = True
        if(data_dict_list[i]["avg_episode_duration"] != "None"):
            data_dict_list[i]["avg_episode_duration"] = round(
                float(data_dict_list[i]["avg_episode_duration"]), 2)
        if(data_dict_list[i]["episode_count"] != "None"):
            data_dict_list[i]["episode_count"] = round(
                float(data_dict_list[i]["episode_count"]))
    if(found_query):
        data_dict_list.pop(index_of_podcast)

    return render_template('search.html', name=project_name, netid=net_id,
                           data=data_dict_list, podcast_names=podcast_names, genres=genres,
                           avg_ep_durations=avg_ep_durations, min_ep_counts=min_ep_counts,
                           query_feedback=query_uncleaned, genre_feedback=genre_query_uncleaned,
                           avg_ep_duration_feedback=avg_ep_duration_query_uncleaned,
                           min_ep_count_feedback=min_ep_count_query_uncleaned, show_modal=True)
