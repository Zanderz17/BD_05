from flask import Blueprint, current_app, jsonify
main = Blueprint('search_python_blueprint', __name__)
import time


@main.route('/<query>/<topk>')
def SearchPython(query, topk):
    start_time = time.time()
    instance = current_app.config['PrincipalClass']

    result_list, execution_time_01 = instance.search(query, topk)

    docs_list = []
    for result in result_list:
        temp_doc = {}
        temp_doc["id"] = result['id'];
        temp_doc["score"] = result['score']
        temp_doc["title"] = result['title']
        docs_list.append(temp_doc)
    end_time = time.time()
    execution_time = end_time - start_time    

    result = {'docs_list': docs_list, 'execution_time': round(execution_time, 3)}
    return jsonify(result)
