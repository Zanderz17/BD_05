from flask import Flask
from flask_cors import CORS
from config import config

# Routes
from routes import NewsDB
from routes import UploadDataPSQL
from routes.pythonIndex import UpdateDataPython
from routes import DeleteObject
from routes import SearchPython

app = Flask(__name__)


# Change according port of frontend
CORS(app, resources={"*": {"origins": "http://localhost:5173"}})

def page_not_found(error):
    return "<h1>Not found page </h1>", 404


if __name__ == '__main__':
    app.config.from_object(config['development'])

    # Blueprints
    app.register_blueprint(NewsDB.main, url_prefix='/api/news')
    app.register_blueprint(UploadDataPSQL.main, url_prefix='/uploadDataPSQL')
    app.register_blueprint(UpdateDataPython.main, url_prefix='/uploadDataPython')
    app.register_blueprint(DeleteObject.main, url_prefix='/deleteObject')
    app.register_blueprint(SearchPython.main, url_prefix='/searchPython')
    # Error handlers
    app.register_error_handler(404, page_not_found)
    app.run()
