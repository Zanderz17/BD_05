from flask import Blueprint, jsonify
import time

# Models
from models.NewsModel import NewsModel

main = Blueprint('news_blueprint', __name__)


@main.route('/<query>/<top_k>')
def get_news_query(query, top_k):
    start_time = time.time()
    try:
        noticia = NewsModel.get_news_query(query, top_k)
        end_time = time.time()
        execution_time = end_time - start_time

        if noticia != None:
            return jsonify(
                {'noticia': noticia, 'execution_time': round(execution_time,3)})
        else:
            return jsonify({}), 404
    except Exception as ex:
        return jsonify({'message': str(ex)}), 500
