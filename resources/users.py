import json

from flask import jsonify, Blueprint, abort, make_response
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


user_fields = {
    'username': fields.String
}

def user_or_404(user_id):
    try:
        user = models.User.get(models.User.id == user_id)
    except models.User.DoesNotExist:
        abort(404)
    else:
        return user


class UserList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'username',
            required=True,
            help='No username provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'email',
            required=True,
            help='No email provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'password',
            required=True,
            help='Invalid password provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'verify_password',
            required=True,
            help='Invalid password verification provided',
            location=['form', 'json']
        )
        super().__init__()

    def get(sef):
        users = [marshal(user, user_fields)
                    for user in models.User.select()]
        return {'users': users}

    def post(self):
        args = self.reqparse.parse_args()
        if args.get('password') == args.get('verify_password'):
            user = models.User.create_user(**args)
            return marshal(user, user_fields), 201
        return make_response(json.dumps({'error': 'Password and password verification do not match.'}, 400))


class User(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'username',
            required=True,
            help='No username provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'email',
            required=True,
            help='No email provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'password',
            required=True,
            help='Invalid password provided',
            location=['form', 'json']
        )
        super().__init__()

    @marshal_with(user_fields)
    def get(self, id):
        return user_or_404(id)


users_api = Blueprint('resources.users', __name__)
api = Api(users_api)

api.add_resource(
    UserList,
    '/users',
    endpoint = 'users'
)

api.add_resource(
    User,
    '/users/<int:id>',
    endpoint = 'user'
)
