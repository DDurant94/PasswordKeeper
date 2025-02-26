from flask import request, jsonify
from models.schemas.folderSchema import folder_schema,folders_schema
from marshmallow import ValidationError
from caching import cache

from utils.util import token_required, role_required
from services import folderService

def save():
  try:
    folder_data = folder_schema.load(request.json)
  except ValidationError as err:
    return jsonify(err.messages),400
  
  try:
    folder_save = folderService.save(folder_data)
    
    if folder_save is not None:
      return folder_schema.jsonify(folder_save), 201
  
  except ValueError as e:
    return jsonify({"Error": str(e)}),400
  

def find_user_folders(user_id):
  folders = folderService.find_user_folders(user_id)
  
  if folders is not None:
    return folders_schema.jsonify(folders), 200
  
  else:
    return jsonify({"message": "Could not find any folders"}), 400
  
  
def update(folder_name):
  try:
    folder_data = folder_schema.load(request.json)
  except ValidationError as err:
    return jsonify(err.messages), 400
  
  try:
    update_folder = folderService.update(folder_data,folder_name)
    
    if update_folder is not None:
      return folder_schema.jsonify(update_folder), 201
    
  except ValueError as e:
    return jsonify({"Error": str(e)}), 400
  
def delete():
  folder_data = folder_schema.load(request.json)
  
  folder = folderService.delete(folder_data)
  
  if folder == "successful":
    return jsonify({"message": "Folder has be removed!"}), 200
  
  else:
    return jsonify({"message": f"Couldn't find folder '{folder_data['folder_name']}'"}), 404