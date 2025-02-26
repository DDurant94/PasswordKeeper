from sqlalchemy.orm import Session
from database import db
from sqlalchemy import select
from circuitbreaker import circuit
from werkzeug.security import generate_password_hash, check_password_hash
import os
import datetime

from utils.util import encode_token, derive_key

from models.user import User
from models.role import Role
from models.userManagement import UserManagementRole as UMR 

# Fallback function incase of an error
def fallback_function(*user):
  return None

# Adding a new user
@circuit(failure_threshold=1,recovery_timeout=10,fallback_function=fallback_function)
def save(user_data):
  try:
    if user_data['username'] == "Failure":
        raise Exception("Failure condition triggered")
    with Session(db.engine) as session:
      with session.begin():
      
        user = session.execute(db.select(User).where(User.username == user_data['username'])).scalar_one_or_none()
        
        if user:
          raise ValueError("User Already Exists!")
        
        if 'role' not in user_data.keys():
          user_role = "user"
          
        else:
          user_role = user_data['role']
        
        savepoint = session.begin_nested() 
         
        time = datetime.datetime.now()
        salt = os.urandom(16)
        
        new_user = User(username = user_data['username'],
                        password = generate_password_hash(user_data['password']),
                        first_name = user_data['first_name'],
                        last_name = user_data['last_name'],
                        email = user_data['email'],
                        create_date = time,
                        updated_date = time,
                        role = user_role,
                        key = salt)
        session.add(new_user)
        session.flush()
                
        role = db.session.execute(db.select(Role).where(Role.role_name == new_user.role)).scalar_one_or_none()
        
        if role is not None:
          adding_user_to_role = UMR(user_management_id = new_user.user_id, role_id = role.role_id)
          session.add(adding_user_to_role)
        else:
          savepoint.rollback()
          raise ValueError("Role Not Found! Add Role or Change Role")
      
        session.commit()
        
      session.refresh(new_user)
      
    return new_user
  except Exception as e:
    raise e

# Finding user by I.D.
def find_by_id(search_id):
  query = select(User).filter_by(user_id = search_id)
  user = db.session.execute(query).unique().scalar_one_or_none()
  print(user.key)
  return user

# Updating user account
@circuit(failure_threshold=1,recovery_timeout=10,fallback_function=fallback_function)
def update(user_data,username):
  try:
    with Session(db.engine) as session:
      with session.begin():
        user = db.session.execute(db.select(User).where(User.username == username)).unique().scalar_one_or_none()
        
        if user == None:
          raise ValueError(f"User with '{username}' not found!")
        
        time = datetime.datetime.now()
        
        user.first_name = user_data['first_name']
        user.last_name = user_data['last_name']
        user.email = user_data['email']
        user.password = generate_password_hash(user_data['password'])
        user.updated_date = time
      db.session.commit()
    return user
        
  except Exception as e:
    raise e

#log user into account
def login_user(username, password):
  user = (db.session.execute(db.select(User).where(User.username == username)).unique().scalar_one_or_none())
  
  if user:
    if check_password_hash(user.password, password):
      role_names = [role.role_name for role in user.roles]
      auth_token = encode_token(user.user_id, role_names)
      
      resp = {
        "status": "success",
        "message": "Successfully logged in",
        "auth_token": auth_token
      }
      
      return [resp]
    
    else:
      return [None,"Password"]
    
  else:
    return [None,"Username"]

# delete user 
def delete(user_id):
  with Session(db.engine) as session:
    with session.begin():
      user = session.execute(db.select(User).where(User.user_id == user_id)).unique().scalar_one_or_none()
      if user:
        session.delete(user)
      else:
        return None
      
    session.commit()
  return "successful"
  