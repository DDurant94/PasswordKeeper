from sqlalchemy.orm import Session
from database import db
from sqlalchemy import select

from models.role import Role

# Adding a new role to API
def save(role_data):
  with Session(db.engine) as session:
    with session.begin():
      new_role = Role(role_name = role_data['role_name'])
      
      session.add(new_role)
      session.commit()
    session.refresh(new_role)
  return new_role