from fastapi import FastAPI, HTTPException,Depends,status
from pydantic import BaseModel
from typing import List,Optional
import models
from database import SessionLocal,engine,conn
from sqlalchemy.orm import Session
from sqlalchemy import or_
app = FastAPI()

models.Base.metadata.create_all(bind=engine)

class ProfileBase(BaseModel):
    profile_image: Optional[str] = None

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(ProfileBase):
    pass


class UserBase(BaseModel):
    username: str
    password: str
    email: str
    phone: str

class UserCreate(UserBase):
    profile: Optional[ProfileCreate] = None

class UserUpdate(UserBase):
    profile: Optional[ProfileUpdate] = None

class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    profile: Optional[ProfileBase] = None

    class Config:
        orm_mode = True




def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# db_dependency = Annotated[Session,Depends(get_db)]




@app.post("/users/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if email or phone already exists
    existing_user = db.query(models.User).filter(or_(models.User.email == user.email, models.User.phone == user.phone)).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or phone already exists")

    # Save user data in PostgreSQL
    profile_data = user.profile
    user_data = user.dict(exclude={"profile"})
    db_user = models.User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    user_id = db_user.id

    # Save user ID and profile picture in MongoDB
    mongo_user = {"user_id": user_id, "profile_image": profile_data.dict()}  # Convert profile_data to a dictionary
    conn.local.user.insert_one(mongo_user)
    return db_user





@app.get("/users/", response_model=List[dict])
def list_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    user_list = []
    for user in users:
        # Retrieve profile_image from MongoDB using user_id
        mongo_user = conn.local.user.find_one({"user_id": user.id})
        if mongo_user:
            user_id = mongo_user.get("user_id")
            profile_image = mongo_user.get("profile_image")
        else:
            user_id = None
            profile_image = None

        # Create dictionary with user data and profile_image
        user_data = {
            "id": user.id,
            "name": user.username,
            "phone": user.phone,
            "email": user.email,
            "user_id": user_id,
            "profile_data": profile_image,
        }

        user_list.append(user_data)

    return user_list






@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    # Retrieve the user from PostgreSQL
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Update the user data in PostgreSQL
    if user.username:
        db_user.name = user.username
    if user.email:
        db_user.email = user.email
    # Update other user fields as needed

    # Update the profile image in MongoDB
    mongo_user = conn.local.user.find_one({"user_id": user_id})
    if not mongo_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    if user.profile and user.profile.profile_image:
        profile_image = user.profile.profile_image
        mongo_user["profile_image"] = str(profile_image)
        conn.local.user.replace_one({"user_id": user_id}, mongo_user)

    db.commit()

    return db_user




@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    # Delete the user from PostgreSQL
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(db_user)
    db.commit()

    # Delete the user's profile from MongoDB
    conn.local.user.delete_one({"user_id": user_id})

    return {"message": "User deleted successfully"}
