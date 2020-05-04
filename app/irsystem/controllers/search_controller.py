from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from app.irsystem.models.podcasts import Podcasts
from app.irsystem.controllers.similarity_calculator import *
from app.irsystem.controllers.query_db import *


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


def cleanData(data_dict_list, review_lst):
    for i in range(len(data_dict_list)):
        data_dict_list[i]['reviews'] = list(
            filter(lambda x: x["pod_name"] == data_dict_list[i]['name'], review_lst))
        if(data_dict_list[i]["avg_episode_duration"] != "None"):
            data_dict_list[i]["avg_episode_duration"] = round(
                float(data_dict_list[i]["avg_episode_duration"]), 2)
        if(data_dict_list[i]["episode_count"] != "None"):
            data_dict_list[i]["episode_count"] = round(
                float(data_dict_list[i]["episode_count"]))
    return data_dict_list


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

    randomPodcast = getRandomHighlyRated()
    # print(randomPodcast)

    if not query:
        data_dict_list = []
        queryPodcastData = []
    else:
        if advancedQueryIsEnabled:
            podcast_lst = advancedPodcastData(
                genre_query, min_ep_count_query, avg_ep_duration_query[0], avg_ep_duration_query[1])
        else:
            podcast_lst = getPodcastData()
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

        pod_name_to_idx_review_dict = {}
        for (idx, review) in enumerate(review_lst):
            try:
                pod_name_to_idx_review_dict[review["pod_name"]
                                            ] = pod_name_to_idx_review_dict[review["pod_name"]] + [idx]
            except KeyError:
                pod_name_to_idx_review_dict[review["pod_name"]] = [idx]

        queryPodcastData = getPodcastData(query)

        data_dict_list = get_ranked_podcast(queryPodcastData[0],
                                            podcast_lst, review_lst, pod_name_to_idx_review_dict,
                                            genre_query,
                                            advancedQueryDict["genre"],
                                            advancedQueryDict["avg_ep_duration"],
                                            advancedQueryDict["min_ep_count"])

        data_dict_list = cleanData(data_dict_list, review_lst)
        if(len(queryPodcastData) > 0):
            queryPodcastData = cleanData(queryPodcastData, review_lst)
        data_dict_list = removeQueryFromData(data_dict_list, query)

        # if luckyPodcast:
        #     data_dict_list = getPodcastData(randomPodcast)[0]
        #     queryPodcastData = []

    return render_template('search.html', name=project_name, netid=net_id,
                           data=data_dict_list, podcast_names=podcast_names, genres=genres,
                           avg_ep_durations=avg_ep_durations, min_ep_counts=min_ep_counts,
                           query_feedback=query_uncleaned, genre_feedback=genre_query_uncleaned,
                           avg_ep_duration_feedback=avg_ep_duration_query_uncleaned,
                           min_ep_count_feedback=min_ep_count_query_uncleaned,
                           query_podcast_data=queryPodcastData, show_modal=True)
