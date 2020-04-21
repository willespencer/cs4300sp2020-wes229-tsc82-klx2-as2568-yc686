from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from app.irsystem.models.podcasts import Podcasts
from app.irsystem.models.reviews import Reviews
from app.irsystem.controllers.similarity_calculator import *
from sqlalchemy.orm import load_only

project_name = "Find the Pea to your Podcast"
net_id = "Will Spencer: wes229, Theresa Cho: tsc82, Kathleen Xu: klx2, Yvonne Chan: yc686, Akira Shindo: as2568"


@irsystem.route('/', methods=['GET'])
def search():
	# queries all podcasts names
	query_podcast_names = Podcasts.query.order_by(Podcasts.name).options(load_only("name")).all()
	all_podcast_names = []
	for result in query_podcast_names:
		all_podcast_names.append(result.name)
	# print(all_podcast_names)

	# user input query
	query = request.args.get('podcast_search')

	podcast_names = all_podcast_names

	if not podcast:
		data_dict_list = []
	else:
		#formatting list of podcast dicts
		query_all_podcasts = Podcasts.query.all()
		all_podcasts = []
		for result in query_all_podcasts:
			pod_dict = {
				'name': result.name,
				'description': result.description,
				'episode_count': result.ep_count,
				'avg_episode_duration': result.ep_durations,
				'link': result.itunes_url,
				'rating': result.rating
			}
			if result.artwork != None:
				pod_dict['pic'] = result.artwork
			else:
				pod_dict['pic'] = "placeholder.jpg"

			pod_dict['genres'] = (result.genres).split(';')
			all_podcasts.append(pod_dict)
		# print(all_podcasts[0])

		#replace 'Fresh Air' with podcast once the all_podcast_names are intergrated as valid inputs
		# query_podcast_info = Podcasts.query.filter_by(name='Fresh Air').first_or_404()
		query_reviews = Reviews.query.filter_by(pod_name=query).all()

		query_podcast_info = Podcasts.query.filter_by(name=query).first_or_404()
		query_dict = {
			'name': query_podcast_info.name,
			'description': query_podcast_info.description,
			'episode_count': query_podcast_info.ep_count,
			'avg_episode_duration': query_podcast_info.ep_durations,
			'link': query_podcast_info.itunes_url,
			'rating': query_podcast_info.rating
		}
		if query_podcast_info.artwork != None:
			query_dict['pic'] = query_podcast_info.artwork
		else:
			query_dict['pic'] = "placeholder.jpg"

		query_dict['genres'] = (query_podcast_info.genres).split(';')

		#formatting list of podcast reviews dicts for query
		all_reviews = []
		for review in query_reviews:
			review_dict = {
				'pod_name': review.pod_name,
				'rev_name': review.review_name,
				'rev_rating': review.review_rating,
				'rev_text': review.review_text
			}
			all_reviews.append(review_dict)
		# print(all_reviews[0])

		# calculates similarity scores
		# data_dict_list = get_ranked_podcast(query_dict, all_podcasts, all_reviews)

		# data_dict_list = [{
		# "pic": "http://is1.mzstatic.com/image/thumb/Music118/v4/8e/52/e1/8e52e12c-1bf4-0d48-8aeb-97d7a0c55582/source/100x100bb.jpg",
		# "name": "Myths and Legends",
		# "description": "Jason Weiser tells stories from myths, legends, and folklore that have shaped cultures throughout history. Some, like the stories of Aladdin, King Arthur, and Hercules are stories you think you know, but with surprising origins. Others are stories you might not have heard, but really should. All the stories are sourced from world folklore, but retold for modern ears. These are stories of wizards, knights, Vikings, dragons, princesses, and kings from the time when the world beyond the map was a dangerous and wonderful place.",
		# "episode_count": "40",
		# "avg_episode_duration": "20",
		# "link": "https://www.stitcher.com/podcast/jason-weiser/myths-and-legnen",
		# "similarity": "99",
		# "rating": "4.0",
		# "genres": ["Literature", "Fantasy"],
		# "similarities": [("Duration", "TBD"), ("No. Episodes", "TBD"), ("Genre", "TBD"), ("Description", "100")]},
		# {
		# "pic": "placeholder.jpg",
		# "name": "Coffee",
		# "description": "A podcast about coffee",
		# "episode_count": "100",
		# "avg_episode_duration": "15",
		# "link": "https://www.stitcher.com/podcast/studio71/coffee-talk-2",
		# "similarity": "5",
		# "rating": "1.5",
		# "genres": ["Food"],
		# "similarities": [("Duration", "15"), ("No. Episodes", "10"), ("Description", "0")]
		# }]

	# remove querried podcast from showing in result list
	index_of_podcast = 0
	found = False
	for i in range(len(data_dict_list)):
		if(data_dict_list[i].name == query):
			index_of_podcast = i
			found = True
			break
	if(found):
		data_dict_list.pop(index_of_podcast)

	return render_template('search.html', name=project_name, netid=net_id, data=data_dict_list, podcast_names=podcast_names, show_modal=False)
