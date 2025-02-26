from flask import request, jsonify
from models.schemas.passwordHistSchema import password_histories_schema, password_history_schema
from models.schemas.passwordSchema import password_search_schema
from marshmallow import ValidationError
from caching import cache

from utils.util import token_required, role_required
from services import passwordHistService

def all_passwords_hist():
  try:
    user_data = password_search_schema.load(request.json)
  except ValidationError as err:
    return jsonify(err.messages),400
  
  try:
    all_history = passwordHistService.find_passwords_history(user_data)
    if all_history is not None:
      return password_histories_schema.jsonify(all_history), 201
  except ValueError as e:
    return jsonify({'Error': str(e)}), 400
  
def password_hist_by_name(search_name):
  try:
    user_data = password_search_schema.load(request.json)
  except ValidationError as err:
    return jsonify(err.messages),400
  
  try:
    history = passwordHistService.find_password_history(user_data,search_name)
    if history is not None:
      return password_histories_schema.jsonify(history), 201
  except ValueError as e:
    return jsonify({'Error': str(e)}), 400
  