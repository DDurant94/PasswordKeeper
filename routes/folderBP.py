from flask import Blueprint

from controllers.folderController import save, find_user_folders, update, delete

folder_blueprint = Blueprint('folder_bp', __name__)
folder_blueprint.route('/create', methods = ['POST'])(save)
folder_blueprint.route('/<int:user_id>',methods= ['GET'])(find_user_folders)
folder_blueprint.route('/<string:folder_name>',methods= ['PUT'])(update)
folder_blueprint.route('/',methods= ['DELETE'])(delete)