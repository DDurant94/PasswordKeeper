from flask import request, jsonify
from models.schemas.userSchema import user_schema,users_schema
from marshmallow import ValidationError
from caching import cache

from utils.util import token_required, role_required
from services import userService 


def save():
  try:
    user_data = user_schema.load(request.json)
    
  except ValidationError as err:
    return jsonify(err.messages),400
  try:
    user_save = userService.save(user_data)
    if user_save is not None:
      return user_schema.jsonify(user_save),201
    else:
      return jsonify({"message": "Wait 10 seconds and try again!", "body":user_data}),400
  except ValueError as e:
    return jsonify({"Error": str(e)}),400
  
def find_by_id(search_id):
  user = userService.find_by_id(search_id)
  
  if user is not None:
    return user_schema.jsonify(user), 200
  
  else:
    return jsonify({"messages": f"User with I.D. Number {search_id} is not found!", "body": user}), 400
  
def update(username):
  try:
    user_data = user_schema.load(request.json) 
  except ValidationError as err:
    return jsonify(err.messages), 400
  
  try:
    updated_user = userService.update(user_data,username)
    
    if updated_user is not None:
      return user_schema.jsonify(updated_user), 201
    
    else:
      return jsonify({"message": "Wait 10 seconds and try again!", "body":"Use a different username."}),400
    
  except ValueError as e:
     return jsonify({"Error": str(e)}),400
   
def login_user():
  user_data = request.json
  
  user = userService.login_user(user_data['username'], user_data['password'])
  
  if user[0]:
    return jsonify(user[0]), 200
  
  else:

    resp = {
      "status": "Error",
      "message": f"Invalid {user[1]}"
    }
      
    return jsonify(resp), 400
  
  
def delete(user_id):
  user = userService.delete(user_id)
  
  if user == "successful":
    return jsonify({"message": "User removed successfully"}), 200
  else:
    return jsonify({"message": f"Couldn't find User with ID {user_id}"}), 404 