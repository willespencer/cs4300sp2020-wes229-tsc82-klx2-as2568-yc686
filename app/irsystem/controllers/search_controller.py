from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from app.irsystem.models.podcasts import Podcasts
from app.irsystem.models.reviews import Reviews

project_name = "Find the Pea to your Podcast"
net_id = "Will Spencer: wes229, Theresa Cho: tsc82, Kathleen Xu: klx2, Yvonne Chan: yc686, Akira Shindo: as2568"


@irsystem.route('/', methods=['GET'])
def search():
    query = request.args.get('search')

    print(query)
    if not query:
        data = []
        output_message = ''
    else:
        podcast_info = Podcasts.query.filter_by(name=query).first_or_404()

        all_podcasts = Podcasts.query.all()
        print(all_podcasts)

        review_info = Reviews.query.filter_by(name=query).first_or_404()

        output_message = "Your search: " + query
        data = range(5)
    return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)
