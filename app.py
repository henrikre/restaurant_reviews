from flask import Flask

import config
import models

from resources.restaurants import restaurants_api
from resources.reviews import reviews_api

app = Flask(__name__)

app.register_blueprint(restaurants_api, url_prefix='/api/v1')
app.register_blueprint(reviews_api, url_prefix='/api/v1')

@app.route('/api/v1')
def greet():
    return 'Welcome to the restaurant review API'


if __name__ == '__main__':
    models.initialize()
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
