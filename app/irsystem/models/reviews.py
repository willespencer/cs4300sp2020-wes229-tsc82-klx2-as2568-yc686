from . import *


class Reviews(Base):
    __tablename__ = 'reviews'

    pod_name = db.Column(db.String, nullable=False)
    review_name = db.Column(db.String, nullable=False)
    review_rating = db.Column(db.VARCHAR, nullable=False)
    review_text = db.Column(db.String, nullable=False)

    def __init__(self, **kwargs):
        super(Reviews, self).__init__(**kwargs)
        self.pod_name = kwargs.get('pod_name', None)
        self.review_name = kwargs.get('review_name', None)
        self.review_rating = kwargs.get('review_rating', None)
        self.review_text = kwargs.get('review_text', None)

    def __repr__(self):
        return '<Review %r>' % self.pod_name


class ReviewsSchema(ModelSchema):
    class Meta:
        model = Reviews
