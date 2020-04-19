from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

project_name = "Find the Pea to your Podcast"
net_id = "Will Spencer: wes229, Theresa Cho: tsc82, Kathleen Xu: klx2, Yvonne Chan: yc686, Akira Shindo: as2568"


@irsystem.route('/', methods=['GET'])
def search():
	query = request.args.get('podcast_search')
	if not query:
		data = []
		data_dict_list = []
		output_message = ''
	else:
		output_message = "Your search: " + query
		data_dict_list = [{
		"pic": "myth.jpg",
		"name": "Myths and Legends",
		"author": "Anne",
		"description": "Jason Weiser tells stories from myths, legends, and folklore that have shaped cultures throughout history. Some, like the stories of Aladdin, King Arthur, and Hercules are stories you think you know, but with surprising origins. Others are stories you might not have heard, but really should. All the stories are sourced from world folklore, but retold for modern ears. These are stories of wizards, knights, Vikings, dragons, princesses, and kings from the time when the world beyond the map was a dangerous and wonderful place.",
		"episode_count": "40",
		"avg_episode_duration": "20",
		"link": "https://www.stitcher.com/podcast/jason-weiser/myths-and-legnen",
		"similarity": "99",
		"iTunes": "4.0",
		"genres": ["Literature", "Fantasy"],
		"similarities": [("Duration", "80"), ("No. Episodes", "100"), ("Genre", "100"), ("Description", "100")]
	},
	{
		"pic": "coffee.jpg",
		"name": "Coffee",
		"author": "Joe",
		"description": "A podcast about coffee",
		"episode_count": "100",
		"avg_episode_duration": "15",
		"link": "https://www.stitcher.com/podcast/studio71/coffee-talk-2",
		"similarity": "5",
		"iTunes": "1.5",
		"genres": ["Food"],
		"similarities": [("Duration", "15"), ("No. Episodes", "10"), ("Description", "0")]
	}]
	data = [["myth.jpg", "Myths and Legends", "Anne", "Jason Weiser tells stories from myths, legends, and folklore that have shaped cultures throughout history. Some, like the stories of Aladdin, King Arthur, and Hercules are stories you think you know, but with surprising origins. Others are stories you might not have heard, but really should. All the stories are sourced from world folklore, but retold for modern ears. These are stories of wizards, knights, Vikings, dragons, princesses, and kings from the time when the world beyond the map was a dangerous and wonderful place.", "40", "20", "https://www.stitcher.com/podcast/jason-weiser/myths-and-legnen", "99"], ["coffee.jpg", "Coffee", "Joe", "A podcast about coffee.", "100", "15", "https://www.stitcher.com/podcast/studio71/coffee-talk-2", "5"]]
	return render_template('search.html', name=project_name, netid=net_id, data=data_dict_list)

@irsystem.route('/modal')
def modal():
	data_dict_list = [{
		"pic": "myth.jpg",
		"name": "Myths and Legends",
		"author": "Anne",
		"description": "Jason Weiser tells stories from myths, legends, and folklore that have shaped cultures throughout history. Some, like the stories of Aladdin, King Arthur, and Hercules are stories you think you know, but with surprising origins. Others are stories you might not have heard, but really should. All the stories are sourced from world folklore, but retold for modern ears. These are stories of wizards, knights, Vikings, dragons, princesses, and kings from the time when the world beyond the map was a dangerous and wonderful place.",
		"episode_count": "40",
		"avg_episode_duration": "20",
		"link": "https://www.stitcher.com/podcast/jason-weiser/myths-and-legnen",
		"similarity": "99",
		"iTunes": "4.0",
		"genres": ["Literature", "Fantasy"],
		"similarities": [("Duration", "80"), ("No. Episodes", "100"), ("Genre", "100"), ("Description", "100")]
	},
	{
		"pic": "coffee.jpg",
		"name": "Coffee",
		"author": "Joe",
		"description": "A podcast about coffee",
		"episode_count": "100",
		"avg_episode_duration": "15",
		"link": "https://www.stitcher.com/podcast/studio71/coffee-talk-2",
		"similarity": "5",
		"iTunes": "1.5",
		"genres": ["Food"],
		"similarities": [("Duration", "15"), ("No. Episodes", "10"), ("Description", "0")]
	}]
	return render_template('modal.html', data=data_dict_list[0])

# @irsystem.route('/')
# def index():
# 	return render_template('search.html')

# @irsystem.route('/result_list', methods=['GET'])
# def search():
# 	query = request.args.get('podcast_search')
# 	if not query:
# 		data = []
# 		output_message = ''
# 	else:
# 		output_message = "Your search: " + query
# 		data = range(5)
# 	return render_template('result_list.html')

# def render_result(name, author, pic):
# 	return render_template(result.html, name=name, author=author, pic=pic)
