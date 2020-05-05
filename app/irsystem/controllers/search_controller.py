from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from app.irsystem.models.podcasts import Podcasts
from app.irsystem.controllers.similarity_calculator import *
from app.irsystem.controllers.query_db import *
from app.irsystem.controllers.inv_idx_new import inv_idx as inv_idx_new
from app.irsystem.controllers.idf_new import idf as idf_new
from app.irsystem.controllers.doc_norms_new import doc_norms as doc_norms_new

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

# remove query from result list


def removeQueryFromData(data_dict_list, query):
    index_of_podcast = 0
    found_query = False
    for i in range(len(data_dict_list)):
        if(data_dict_list[i]['name'] == query):
            index_of_podcast = i
            found_query = True
    if(found_query):
        data_dict_list.pop(index_of_podcast)
    return data_dict_list

# get reviews and round avg durration and episode count


def cleanData(data_dict_list):
    for i in range(len(data_dict_list)):
        all_reviews = [
            {
                'pod_name': data_dict_list[i]['name'],
                'rev_text': data_dict_list[i]['review1'],
                'rev_rating': data_dict_list[i]['score1']
            },
            {
                'pod_name': data_dict_list[i]['name'],
                'rev_text': data_dict_list[i]['review2'],
                'rev_rating': data_dict_list[i]['score2']
            },
            {
                'pod_name': data_dict_list[i]['name'],
                'rev_text': data_dict_list[i]['review3'],
                'rev_rating': data_dict_list[i]['score3']
            },
            {
                'pod_name': data_dict_list[i]['name'],
                'rev_text': data_dict_list[i]['review4'],
                'rev_rating': data_dict_list[i]['score4']
            },
            {
                'pod_name': data_dict_list[i]['name'],
                'rev_text': data_dict_list[i]['review5'],
                'rev_rating': data_dict_list[i]['score5']
            }
        ]
        data_dict_list[i]['reviews'] = all_reviews
        if(data_dict_list[i]["avg_episode_duration"] != "None"):
            data_dict_list[i]["avg_episode_duration"] = round(
                float(data_dict_list[i]["avg_episode_duration"]), 2)
        if(data_dict_list[i]["episode_count"] != "None"):
            data_dict_list[i]["episode_count"] = round(
                float(data_dict_list[i]["episode_count"]))
    return data_dict_list


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

@irsystem.route('/', methods=['GET', 'POST'])
def search():
    # uncleaned user input
    query_uncleaned = request.args.get('podcast_search')
    genre_query_uncleaned = request.args.get('genre_search')
    avg_ep_duration_query_uncleaned = request.args.get('avg_ep_duration')
    min_ep_count_query_uncleaned = request.args.get('min_ep_count')

    # handles if user wants us to recommend podcast
    if request.method == 'POST':
        answer = request.form.get('recommend_podcast')
        if answer == 'recommend_podcast':
            query = getRandomHighlyRated()
    else:
        query = query_uncleaned

    # user inputs and cleaning.
    # Handles case if genre, avg_ep_duration, min_ep_count not inputted
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
        queryPodcastData = []
    else:
        if advancedQueryIsEnabled:
            podcast_lst = advancedPodcastData(
                genre_query, min_ep_count_query, avg_ep_duration_query[0], avg_ep_duration_query[1])
        else:
            podcast_lst = getPodcastData()
            # print(podcast_lst[:10])
            

        # TODO: recompute idf, inv_idx, doc_norms based on new order

        # calculates similarity scores

        # accum a list of all reviews for every podcast in podcast_lst and the query podcast
        # initially gets all podcast reviews

        podcast_lst_names = [query] + [podcast["name"]
                                       for podcast in podcast_lst]


        # global inv_idx
        # global idf
        # global doc_norms

        if advancedQueryIsEnabled:
            inv_idx = build_inverted_index(podcast_lst)  # dict
            idf = compute_idf(inv_idx, len(podcast_lst))  # dict
            inv_idx = {key: val for key, val in inv_idx.items() if key in idf}   
            doc_norms = compute_doc_norms(inv_idx, idf, len(podcast_lst))  # list
        else:
            inv_idx = inv_idx_new
            idf = idf_new
            doc_norms = doc_norms_new

        queryPodcastData = getPodcastData(query)
        data_dict_list = get_ranked_podcast(queryPodcastData[0], podcast_lst,
            genre_query,
            inv_idx,
            idf,
            doc_norms,
            advancedQueryDict["genre"],
            advancedQueryDict["avg_ep_duration"],
            advancedQueryDict["min_ep_count"])


        data_dict_list = cleanData(data_dict_list)
        if(len(queryPodcastData) > 0):
            queryPodcastData = cleanData(queryPodcastData)
        data_dict_list = removeQueryFromData(data_dict_list, query)

    return render_template('search.html', name=project_name, netid=net_id,
                           data=data_dict_list, podcast_names=podcast_names, genres=genres,
                           avg_ep_durations=avg_ep_durations, min_ep_counts=min_ep_counts,
                           query_feedback=query, genre_feedback=genre_query_uncleaned,
                           avg_ep_duration_feedback=avg_ep_duration_query_uncleaned,
                           min_ep_count_feedback=min_ep_count_query_uncleaned,
                           query_podcast_data=queryPodcastData, show_modal=True)
