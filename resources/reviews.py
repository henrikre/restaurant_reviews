from flask import Blueprint, abort
from flask_restful import (
    Resource,
    Api,
    reqparse,
    inputs,
    fields,
    marshal,
    marshal_with,
    url_for
)

import models


review_fields = {
    'id': fields.Integer,
    'for_restaurant': fields.String,
    'rating': fields.Integer,
    'comment': fields.String(default=''),
    'created_at': fields.DateTime
}


def add_restaurant(review):
    review.for_restaurant = url_for('resources.restaurants.restaurant', id=review.restaurant.id)
    return review

def review_or_404(review_id):
    try:
        review = models.Review.get(models.Review.id == review_id)
    except models.Review.DoesNotExist:
        abort(404)
    else:
        return review


class ReviewList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'restaurant',
            required=True,
            help='No restaurant provided',
            location=['form', 'json'],
            type=inputs.positive
        )
        self.reqparse.add_argument(
            'rating',
            required=True,
            help='Rating should be a number between 1 and 5',
            location=['form', 'json'],
            type=inputs.int_range(1,5)
        )
        self.reqparse.add_argument(
            'comment',
            required=False,
            nullable=True,
            location=['form', 'json'],
            default=''
        )
        super().__init__()

    def get(self):
        reviews = [marshal(add_restaurant(review), review_fields)
                    for review in models.Review.select()]
        return {'reviews': reviews}

    @marshal_with(review_fields)
    def post(self):
        args = self.reqparse.parse_args()
        review = models.Review.create(**args)
        return add_restaurant(review)


class Review(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'restaurant',
            required=True,
            help='No restaurant provided',
            location=['form', 'json'],
            type=inputs.positive
        )
        self.reqparse.add_argument(
            'rating',
            required=True,
            help='Rating should be a number between 1 and 5',
            location=['form', 'json'],
            type=inputs.int_range(1,5)
        )
        self.reqparse.add_argument(
            'comment',
            required=False,
            nullable=True,
            location=['form', 'json'],
            default=''
        )
        super().__init__()

    @marshal_with(review_fields)
    def get(self, id):
        return add_restaurant(review_or_404(id))

    def put(self, id):
        args = self.reqparse.parse_args()
        try:
            review = models.Review.select().where(
                models.Review.id == id
            ).get()
        except models.Review.DoesNotExist:
            return make_response(json.dumps(
                {'error': 'That review does not exist or is not editable'}
            ), 403)

        query = review.update(**args)
        query.execute()
        review = add_restaurant(review_or_404(id))
        return review, 200, {'Location': url_for('resources.reviews.review', id=id)}

    def delete(self, id):
        try:
            review = models.Review.select().where(
                models.Review.created_by == g.user,
                models.Review.id == id
            ).get()
        except models.Review.DoesNotExist:
            return make_response(json.dumps(
                {'error': 'That review does not exist or is not editable'}
            ), 403)
        query = review.delete()
        query.execute()
        return '', 204, {'Location': url_for('resources.reviews')}


reviews_api = Blueprint('resources.reviews', __name__)
api = Api(reviews_api)

api.add_resource(
    ReviewList,
    '/reviews',
    endpoint = 'reviews'
)

api.add_resource(
    Review,
    '/reviews/<int:id>',
    endpoint = 'review'
)
