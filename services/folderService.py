from sqlalchemy.orm import Session
from database import db
from sqlalchemy import select
from circuitbreaker import circuit
import os
import datetime


from utils.util import find_user
from models.folder import Folder

# add a folder
def save(folder_data):
  try:
    with Session(db.engine) as session:
      with session.begin():
        user = find_user(folder_data['user_id'])
        folder = session.execute(db.select(Folder).where(Folder.folder_name == folder_data['folder_name'],
                                                         Folder.user_id == user.user_id)).scalar_one_or_none()

        if folder:
          raise ValueError("Folder name should be unique")
        
        if folder_data['parent_folder_id'] is not None:
          parent_folder = session.execute(db.select(Folder).where(Folder.folder_id == folder_data['parent_folder_id'],
                                                                  Folder.user_id == user.user_id)).scalar_one_or_none()
          
          if parent_folder is None:
            raise ValueError("Parent folder doesn't exist")
                      
        new_folder = Folder(
          user_id = user.user_id,
          parent_folder_id = folder_data['parent_folder_id'],
          folder_name = folder_data['folder_name'].title(),
          created_date = datetime.datetime.now()
        )
        
        session.add(new_folder)
        session.commit()
        
      session.refresh(new_folder)
      
    return new_folder
    
  except Exception as e:
    raise e
  
# find all folders with the user I.D.
def find_user_folders(user_id):
  user = find_user(user_id) 
  folders = db.session.query(Folder).filter(Folder.user_id == user.user_id).order_by(Folder.parent_folder_id).all()
  return folders

# update folder with user I.D. and folder name
def update(folder_data, folder_name):
  with Session(db.engine) as session:
    with session.begin():
      user = find_user(folder_data['user_id'])
      folder = session.query(Folder).filter(Folder.folder_name == folder_name,
                                            Folder.user_id == user.user_id).one_or_none()
      
      if not folder:
        raise ValueError("Folder not found!")
      
      if folder_data['folder_name']:
        existing_folder = session.query(Folder).filter(Folder.folder_name == folder_data['folder_name'],
                                                       Folder.user_id == user.user_id).one_or_none()
        
        if existing_folder and existing_folder.folder_id != folder.folder_id:
            raise ValueError("Folder name should be unique")
          
        folder.folder_name = folder_data['folder_name']
      
      if folder_data['parent_folder_id'] is not None:
        parent_folder = session.query(Folder).filter(Folder.folder_id == folder_data['parent_folder_id'],
                                                     Folder.user_id == user.user_id).one_or_none()
          
        if parent_folder is None:
          raise ValueError("Parent folder doesn't exist")
          
        folder.parent_folder_id = folder_data['parent_folder_id']
        
      else:
        folder.parent_folder_id = None
      
      for child in folder.children_folders:
        child.parent_folder_id = folder.folder_id
      
      session.commit()
      
    session.refresh(folder)
      
  return folder

# delete folder
def delete(folder_data):
  with Session(db.engine) as session:
    with session.begin():
      user = find_user(folder_data['user_id'])
      folder = session.execute(db.select(Folder).where(Folder.folder_name == folder_data['folder_name'],
                                              Folder.user_id == user.user_id,
                                              Folder.folder_id == folder_data['folder_id'])).unique().scalar_one_or_none()
      
      if not folder:
        return None
      
      session.delete(folder)
      session.commit()
  return "successful"