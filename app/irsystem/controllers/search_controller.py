from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from app.irsystem.models.podcasts import Podcasts
from app.irsystem.controllers.similarity_calculator import *
from app.irsystem.controllers.query_db import *


project_name = "Find the Pea to your Podcast"
net_id = "Will Spencer: wes229, Theresa Cho: tsc82, Kathleen Xu: klx2, Yvonne Chan: yc686, Akira Shindo: as2568"


@irsystem.route('/', methods=['GET'])
def search():
    # user input query
    query = request.args.get('podcast_search')

    # Note: the order changes everytime it's queried for some reason
    podcast_names = getAllPodcastNames()
    genres = getAllGenres()

    max_ep_dur = db.session.query(db.func.max(Podcasts.ep_durations)).scalar()
    min_ep_dur = db.session.query(
        db.func.min(Podcasts.ep_durations)).scalar()
    max_ep_count = db.session.query(db.func.max(Podcasts.ep_count)).scalar()
    min_ep_count = db.session.query(
        db.func.min(Podcasts.ep_count)).scalar()
    # print(max_ep_count)
    # print(min_ep_count)
    # print(max_ep_dur)
    # print(min_ep_dur)

    if not query:
        data_dict_list = []
    else:
        # if advancedQuery enabled
        # advancedQuery = advancedPodcastData(
        #     "Literature", 10, 10, 5)
        # print(advancedQuery)
        # print(len(advancedQuery))

        # calculates similarity scores
        data_dict_list = get_ranked_podcast(getPodcastData(
            query)[0], getPodcastData(), getPodcastReviews(query))

    # remove querried podcast from showing in result list, and round avg durration and episode count
    index_of_podcast = 0
    found_query = False
    for i in range(len(data_dict_list)):
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

    return render_template('search.html', name=project_name, netid=net_id, data=data_dict_list, podcast_names=podcast_names, show_modal=True)
