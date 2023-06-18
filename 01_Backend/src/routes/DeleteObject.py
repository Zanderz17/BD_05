from flask import Blueprint, current_app, jsonify
main = Blueprint('delete_blueprint', __name__)


@main.route('/')
def DeletePython():
    instance = current_app.config['PrincipalClass']
    instance.clean_directories()
    del current_app.config['PrincipalClass']
    result = {'mensaje': 'Objeto principal borrado con éxito', 'resultado':True}
    return jsonify(result)
