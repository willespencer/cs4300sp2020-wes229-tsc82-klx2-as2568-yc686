from app import db, Flask, SQLAlchemy
from . import *


class Podcasts(Base):
    __tablename__ = 'podcasts'

    name = db.Column(db.String, nullable=False)
    rating_volume = db.Column(db.VARCHAR, nullable=False)
    rating = db.Column(db.VARCHAR, nullable=False)
    description = db.Column(db.String, nullable=False)
    artwork = db.Column(db.VARCHAR, nullable=False)
    genres = db.Column(db.String, nullable=False)
    ep_count = db.Column(db.VARCHAR, nullable=False)
    ep_durations = db.Column(db.VARCHAR, nullable=False)
    itunes_url = db.Column(db.VARCHAR, nullable=False)
    feed_url = db.Column(db.VARCHAR, nullable=False)
    podcast_url = db.Column(db.VARCHAR, nullable=False)

    def __init__(self, **kwargs):
        super(Podcasts, self).__init__(**kwargs)
        self.name = kwargs.get('name', None)
        self.rating_volume = kwargs.get('rating_volume', None)
        self.rating = kwargs.get('rating', None)
        self.genres = kwargs.get('genres', None)
        self.description = kwargs.get('description_x', None)
        self.artwork = kwargs.get('artwork', None)
        self.ep_count = kwargs.get('ep_count', None)
        self.ep_durations = kwargs.get('ep_durations', None)
        self.itunes_url = kwargs.get('itunes_url', None)
        self.feed_url = kwargs.get('feed_url', None)
        self.podcast_url = kwargs.get('podcast_url', None)

    def __repr__(self):
        return '<Podcast %r>' % self.name


class PodcastSchema(ModelSchema):
    class Meta:
        model = Podcasts
