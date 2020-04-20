from app import db, Flask, SQLAlchemy
from . import *


class Podcasts(Base):
    __tablename__ = 'podcasts'

    name = db.Column(db.String, nullable=False)
    rating_volume = db.Column(db.VARCHAR, nullable=False)
    rating = db.Column(db.VARCHAR, nullable=False)
    genre = db.Column(db.String, nullable=False)
    description_x = db.Column(db.String, nullable=False)
    artwork = db.Column(db.VARCHAR, nullable=False)
    genres = db.Column(db.String, nullable=False)
    ep_count = db.Column(db.VARCHAR, nullable=False)
    ep_durations = db.Column(db.VARCHAR, nullable=False)
    itunes_url = db.Column(db.VARCHAR, nullable=False)
    feed_url = db.Column(db.VARCHAR, nullable=False)
    podcast_url = db.Column(db.VARCHAR, nullable=False)
    description_y = db.Column(db.String, nullable=False)

    def __init__(self, **kwargs):
        self.name = kwargs.get('name', None)
        self.rating_volume = kwargs.get('rating_volume', None)
        self.rating = kwargs.get('rating', None)
        self.genre = kwargs.get('genre', None)
        self.genres = kwargs.get('genres', None)
        self.description_x = kwargs.get('description_x', None)
        self.description_y = kwargs.get('description_y', None)
        self.artwork = kwargs.get('artwork', None)
        self.ep_count = kwargs.get('ep_count', None)
        self.ep_durations = kwargs.get('ep_durations', None)
        self.itunes_url = kwargs.get('itunes_url', None)
        self.feed_url = kwargs.get('feed_url', None)
        self.podcast_url = kwargs.get('podcast_url', None)

    def __repr__(self):
        return str(self.__dict__)


class PodcastSchema(ModelSchema):
    class Meta:
        model = Podcasts
