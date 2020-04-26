from app import db, Flask, SQLAlchemy
from . import *


class Podcasts(Base):
    __tablename__ = 'podcasts'

    name = db.Column(db.String, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)
    artwork = db.Column(db.VARCHAR, nullable=False)
    genres = db.Column(db.String, nullable=False)
    ep_count = db.Column(db.Integer, nullable=False)
    ep_durations = db.Column(db.Integer, nullable=False)
    itunes_url = db.Column(db.VARCHAR, nullable=False)
    podcast_url = db.Column(db.VARCHAR, nullable=True)
    score_1 = db.Column(db.Integer, nullable=True)
    review_1 = db.Column(db.VARCHAR, nullable=True)
    score_2 = db.Column(db.Integer, nullable=True)
    review_2 = db.Column(db.VARCHAR, nullable=True)
    score_3 = db.Column(db.Integer, nullable=True)
    review_3 = db.Column(db.VARCHAR, nullable=True)
    score_4 = db.Column(db.Integer, nullable=True)
    review_4 = db.Column(db.VARCHAR, nullable=True)
    score_5 = db.Column(db.Integer, nullable=True)
    review_5 = db.Column(db.VARCHAR, nullable=True)

    def __init__(self, **kwargs):
        super(Podcasts, self).__init__(**kwargs)
        self.name = kwargs.get('name', None)
        self.rating = kwargs.get('rating', None)
        self.genres = kwargs.get('genres', None)
        self.description = kwargs.get('description_x', None)
        self.artwork = kwargs.get('artwork', None)
        self.ep_count = kwargs.get('ep_count', None)
        self.ep_durations = kwargs.get('ep_durations', None)
        self.itunes_url = kwargs.get('itunes_url', None)
        self.podcast_url = kwargs.get('podcast_url', None)
        self.score_1 = kwargs.get('score_1', None)
        self.review_1 = kwargs.get('review_1', None)
        self.score_2 = kwargs.get('score_2', None)
        self.review_2 = kwargs.get('review_2', None)
        self.score_3 = kwargs.get('score_3', None)
        self.review_3 = kwargs.get('review_3', None)
        self.score_4 = kwargs.get('score_4', None)
        self.review_4 = kwargs.get('review_4', None)
        self.score_5 = kwargs.get('score_5', None)
        self.review_5 = kwargs.get('review_5', None)

    def __repr__(self):
        return str(self.__dict__)


class PodcastSchema(ModelSchema):
    class Meta:
        model = Podcasts
