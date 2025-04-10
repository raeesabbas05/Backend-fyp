from sqlalchemy import Column, Integer, String, Float
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# database models
class User(db.Model):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    firstname = Column(String(50))
    lastname = Column(String(50))
    email = Column(String(200), unique=True, nullable=False)
    password = Column(String(250), nullable=False)
