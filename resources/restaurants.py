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


restaurant_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'reviews': fields.List(fields.String)
}


def restaurant_or_404(restaurant_id):
    try:
        restaurant = models.Restaurant.get(models.Restaurant.id == restaurant_id)
    except models.Restaurant.DoesNotExist:
        abort(404)
    else:
        return restaurant

def add_reviews(restaurant):
    restaurant.reviews = [url_for('resources.reviews.review', id=review.id)
                            for review in restaurant.review_set]
    return restaurant


class RestaurantList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'name',
            required=True,
            help='No restaurant name provided',
            location=['form', 'json']
        )
        super().__init__()

    def get(self):
        restaurants = [marshal(add_reviews(restaurant), restaurant_fields)
                        for restaurant in models.Restaurant.select()]
        return {'restaurants': restaurants}

    @marshal_with(restaurant_fields)
    def post(self):
        args = self.reqparse.parse_args()
        restaurant = models.Restaurant.create(**args)
        return restaurant, 201


class Restaurant(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'name',
            required=True,
            help='No restaurant name provided',
            location=['form', 'json']
        )
        super().__init__()

    @marshal_with(restaurant_fields)
    def get(self, id):
        return add_reviews(restaurant_or_404(id))

    @marshal_with(restaurant_fields)
    def put(self, id):
        args = self.reqparse.parse_args()
        query = models.Restaurant.update(**args).where(models.Restaurant.id == id)
        query.execute()
        return models.Restaurant.get(models.Restaurant.id == id), 200

    def delete(self, id):
        query = models.Restaurant.delete().where(models.Restaurant.id == id)
        query.execute()
        return '', 204


restaurants_api = Blueprint('resources.restaurants', __name__)
api = Api(restaurants_api)

api.add_resource(
    RestaurantList,
    '/restaurants',
    endpoint = 'restaurants'
)

api.add_resource(
    Restaurant,
    '/restaurants/<int:id>',
    endpoint = 'restaurant'
)
