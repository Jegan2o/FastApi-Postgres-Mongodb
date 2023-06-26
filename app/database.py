from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

"""
PostgreSQL connection
"""
DATABASE_URL = "postgresql://postgres:office@localhost/demo"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base = declarative_base()


##########################################################################################

"""
MongoDB connection
"""
from pymongo import MongoClient
conn = MongoClient()