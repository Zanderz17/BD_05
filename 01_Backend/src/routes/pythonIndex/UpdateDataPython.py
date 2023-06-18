from flask import Blueprint, current_app, jsonify
import time

from routes.principalClass.TextRetriever import TextRetriever
############## Flask Implementation #####################
main = Blueprint('marcelo_blueprint', __name__)

class ArticleXivi():
      def __init__(self, id=None, title=None, rank=None) -> None:
            self.id = id,
            self.title = title
            self.rank = rank

      def to_JSON(self):
            return {
                  'id': self.id,
                  'title': self.title,
                  'rank': self.rank
            }

@main.route('/<size>')
def UpdateDataPython(size):
    start_time = time.time()
    current_app.config['PrincipalClass'] = TextRetriever()
    instance = current_app.config['PrincipalClass']
    instance.clean_directories()
    instance.docs_to_read = size
    instance.load_data() # process the dataset
    end_time = time.time()
    execution_time = end_time - start_time

    result = {'mensaje': f'Objeto principal con {size} documentos creado con éxito', 'execution_time': round(execution_time, 3)}
    return jsonify(result)
