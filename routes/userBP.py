from flask import Blueprint

from controllers.userController import save, find_by_id, update, login_user, delete

user_blueprint = Blueprint('user_bp', __name__)
user_blueprint.route('/create_user',methods=['POST'])(save)
user_blueprint.route('/<int:search_id>',methods=['GET'])(find_by_id)
user_blueprint.route('/<string:username>/update',methods=['PUT'])(update)
user_blueprint.route('/login',methods=['POST'])(login_user)
user_blueprint.route('/delete/<int:user_id>',methods = ['DELETE'])(delete)
