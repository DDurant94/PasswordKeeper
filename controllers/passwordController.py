from flask import request, jsonify
from models.schemas.passwordSchema import password_schema, passwords_schema, password_search_schema
from marshmallow import ValidationError
from caching import cache

from utils.util import token_required, role_required
from services import passwordService

def save():
  try:
    password_data = password_schema.load(request.json)
  except ValidationError as err:
    return jsonify(err.messages),400

  try:
    password_save = passwordService.save(password_data)
    return password_schema.jsonify(password_save), 201
  except ValueError as e:
    return jsonify({'Error': str(e)}), 400
  
def find_passwords():
  try:
    user_data = password_search_schema.load(request.json)
  except ValidationError as err:
    return jsonify(err.messages),400
  
  try:
    passwords = passwordService.find_passwords(user_data)
    if passwords is not None:
      return passwords_schema.jsonify(passwords), 201
  except ValueError as e:
    return jsonify({'Error': str(e)}), 400
  
def find_password(name):
  try:
    user_data = password_search_schema.load(request.json)
  except ValidationError as err:
    return jsonify(err.messages),400
  
  try:
    passwords = passwordService.find_password(user_data,name)
    if passwords is not None:
      return password_schema.jsonify(passwords), 201
  except ValueError as e:
    return jsonify({'Error': str(e)}), 400
  
  
def update(password_id):
  try:
    password_data = password_schema.load(request.json)
  except ValidationError as err:
    return jsonify(err.messages),400

  try:
    password_updated = passwordService.update(password_id,password_data)

    return password_schema.jsonify(password_updated), 201
    
  except ValueError as e:
    return jsonify({'Error': str(e)}), 400
  
def delete():
  password_data = password_schema.load(request.json)
  
  try:
    password = passwordService.delete(password_data)
    
    if password == "successful":
      return jsonify({"message": "Password has be removed!"}), 200
    
    else:
      return jsonify({"message": f"Couldn't find Password '{password_data['password_name']}'"}), 404
    
  except ValueError as e:
    return jsonify({'Error': str(e)}), 400