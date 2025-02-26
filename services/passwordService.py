from sqlalchemy.orm import Session
from sqlalchemy import select
from circuitbreaker import circuit
import os
import datetime
import base64

from database import db

from utils.util import decrypted,encrypted,find_user,make_key

from models.folder import Folder
from models.passwords import Password
from models.user import User

from services.passwordHistService import save as hist_save, delete as hist_delete

##
###
#### HELPER FUNCS
###
##

# adding password data to history
def password_hist_func(password_data,time):
  hist_save(password_data,time)


##
###
#### MAIN FUNCS
###
##

# adding password
def save(password_data):
  with Session(db.engine) as session:
    with session.begin():
      user = find_user(password_data['user_id'])
      
      if password_data['folder_id'] is not None:
        folder = session.query(Folder).filter(Folder.folder_id == password_data['folder_id'],
                                              Folder.user_id == user.user_id).one_or_none()
        
        if folder is None:
          raise ValueError('Folder not found!')
        
      time = datetime.datetime.now()
      key = make_key(user)
      encrypted_password = encrypted(key,password_data['encripted_password'])
      
      new_password = Password(
        folder_id = password_data['folder_id'],
        user_id = user.user_id,
        password_name = password_data['password_name'],
        username = password_data['username'],
        email = password_data['email'],
        encripted_password = encrypted_password,
        created_date = time,
        last_updated_date = time
      )
      
      session.add(new_password)
      session.flush()
      session.commit()
      
    session.refresh(new_password)
    password_hist_func(new_password,time)
  return new_password

# get all passwords
def find_passwords(search_data):
  user = find_user(search_data['user_id'])
  password_data = db.session.query(Password).filter(Password.user_id == user.user_id).all()
  
  key = make_key(user)
  
  for password in password_data:
      password.encripted_password = decrypted(key,password.encripted_password)
  
  return password_data

# get one password
def find_password(user_id, name):
  user = find_user(user_id['user_id'])
  password_data = db.session.query(Password).filter(Password.user_id == user.user_id,
                                                    Password.password_name == name).one_or_none()
  
  if password_data is None:
    raise ValueError(f"'{name}' not found!")
  
  key = make_key(user)
  
  password_data.encripted_password = decrypted(key,password_data.encripted_password)
  
  return password_data

# update password
def update(password_id,password_data):
  try:
    with Session(db.engine) as session:
      with session.begin():
        
        if password_id != password_data['password_id']:
          raise ValueError('Invalid password id!')
        
        user = find_user(password_data['user_id'])
        
        password = session.execute(db.select(Password).where(Password.password_id == password_id, Password.user_id == user.user_id)).scalar_one_or_none()
        
        if password is None:
          raise ValueError('Invalid Password!')
        
        if password_data['folder_id'] is not None:
          folder = session.query(Folder).filter(Folder.folder_id == password_data['folder_id'],
                                              Folder.user_id == user.user_id).one_or_none()
        
          if folder is None:
            raise ValueError('Folder not found!')       
        
        time = datetime.datetime.now()
        key = make_key(user)
        encrypted_password = encrypted(key,password_data['encripted_password'])
        
        password.folder_id = password_data['folder_id']
        password.password_name = password_data['password_name']
        password.username = password_data['username']
        password.email = password_data['email']
        password.encripted_password = encrypted_password
        password.last_updated_date = time
        
        password_hist_func(password,time)
    
        session.commit()
        
      session.refresh(password)
      
    return password
  except Exception as e:
    raise e 

# delete password
def delete(password_data):
  history = hist_delete(password_data)
  
  if history != 'successful':
    return None
  
  with Session(db.engine) as session:
    with session.begin():
      
      password = session.execute(db.select(Password).where(Password.password_id == password_data['password_id'],
                                                           Password.user_id == password_data['user_id'])).unique().scalar_one_or_none()
      
      if not password:
        return None
      
      session.delete(password)
      session.commit()
  return 'successful' 