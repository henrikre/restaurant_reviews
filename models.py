import datetime
import config

from peewee import *

DATABASE = SqliteDatabase('restaurant_reviews.db')


class Restaurant(Model):
    name = CharField(unique=True)
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = DATABASE


class Review(Model):
    restaurant = ForeignKeyField(Restaurant, related_name='review_set')
    rating = IntegerField()
    comment = TextField(default='')
    created_at = DateTimeField(default=datetime.datetime.now)
    # created_by = ForeignKeyField(User, related_name='review_set')

    class Meta:
        database = DATABASE


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([Restaurant, Review], safe=True)
    DATABASE.close()
