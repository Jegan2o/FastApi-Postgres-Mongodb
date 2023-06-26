from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer,primary_key=True)
    username = Column(String,index=True)
    password = Column(String,index=True)
    email = Column(String,index=True)
    phone = Column(String,index=True)
    is_active = Column(Boolean,default=True)
    is_superuser = Column(Boolean,default=False)

#     profile = relationship("Profile",back_populates="user",uselist=False, cascade="all, delete-orphan")

# class Profile(Base):
#     __tablename__ = 'profiles'

#     id = Column(Integer,primary_key=True)
#     user_id = Column(Integer,ForeignKey("users.id"))
#     # store profile image in database
#     profile_image = Column(String,index=True)

#     user = relationship("User",back_populates="profile",uselist=False)

'''
MongoDB model for store profile image'''
# class ProfileImage(Base):
