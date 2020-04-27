from . import *
from app.irsystem.models.podcasts import Podcasts
from sqlalchemy.orm import load_only
from sqlalchemy import func, intersect


def getAllGenres():
    genres = list(Podcasts.query.with_entities(Podcasts.genres))
    all_genres = set()
    for result in genres:
        lst = result.genres.split(';')
        all_genres.update(lst)
    return list(all_genres)


def getAllPodcastNames():
    # queries all podcasts names
    query_podcast_names = Podcasts.query.order_by(
        Podcasts.name).options(load_only("name")).all()
    all_podcast_names = []
    for result in query_podcast_names:
        all_podcast_names.append(result.name)

    return all_podcast_names


def advancedPodcastData(genre=None, min_ep_count=0, max_ep_duration=None, min_ep_duration=0):
    query_podcast_info = db.session.query(Podcasts)
    if genre:
        genre_query = db.session.query(Podcasts).filter(
            Podcasts.genres.like('%' + genre + '%'))
        query_podcast_info = query_podcast_info.intersect(genre_query)
    if max_ep_duration and min_ep_duration:
        ep_dur_query = db.session.query(Podcasts).filter(
            Podcasts.ep_durations > min_ep_duration).filter(Podcasts.ep_durations <= max_ep_duration)
        query_podcast_info = query_podcast_info.intersect(ep_dur_query)
    if min_ep_count:
        ep_count_query = db.session.query(Podcasts).filter(
            Podcasts.ep_count >= min_ep_count)
        query_podcast_info = query_podcast_info.intersect(ep_count_query)

    all_podcasts = []
    for result in query_podcast_info:
        pod_dict = {
            'name': result.name,
            'description': result.description,
            'episode_count': result.ep_count,
            'avg_episode_duration': result.ep_durations,
            'link': result.itunes_url,
            'rating': str(round(float(result.rating), 1))
        }
        if result.artwork != "None":
            pod_dict['pic'] = result.artwork
        else:
            pod_dict['pic'] = "placeholder.jpg"

        pod_dict['genres'] = (result.genres).split(';')
        all_podcasts.append(pod_dict)

    return all_podcasts


def getPodcastData(query="all"):
    # formatting list of podcast dicts
    if query == "all":
        query_podcast_info = Podcasts.query.all()
    else:
        query_podcast_info = [Podcasts.query.filter_by(
            name=query).first_or_404()]

    all_podcasts = []
    for result in query_podcast_info:
        pod_dict = {
            'name': result.name,
            'description': result.description,
            'episode_count': result.ep_count,
            'avg_episode_duration': result.ep_durations,
            'link': result.itunes_url,
            'rating': str(round(float(result.rating), 1))
        }
        if result.artwork != "None":
            pod_dict['pic'] = result.artwork
        else:
            pod_dict['pic'] = "placeholder.jpg"

        pod_dict['genres'] = (result.genres).split(';')
        all_podcasts.append(pod_dict)

    return all_podcasts


def getPodcastReviews(query):
    query_result = Podcasts.query.filter_by(name=query).all()

    # formatting list of podcast reviews dicts for query
    all_reviews = []
    for result in query_result:
        review_dict_1 = {
            'pod_name': result.name,
            'rev_text': result.review_1,
            'rev_rating': result.score_1
        }
        all_reviews.append(review_dict_1)
        review_dict_2 = {
            'pod_name': result.name,
            'rev_text': result.review_2,
            'rev_rating': result.score_2
        }
        all_reviews.append(review_dict_2)
        review_dict_3 = {
            'pod_name': result.name,
            'rev_text': result.review_3,
            'rev_rating': result.score_3
        }
        all_reviews.append(review_dict_3)
        review_dict_4 = {
            'pod_name': result.name,
            'rev_text': result.review_4,
            'rev_rating': result.score_4
        }
        all_reviews.append(review_dict_4)
        review_dict_5 = {
            'pod_name': result.name,
            'rev_text': result.review_5,
            'rev_rating': result.score_5
        }
        all_reviews.append(review_dict_5)

    return all_reviews
