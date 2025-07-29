from sqlalchemy.orm import Session
from sqlalchemy import select
from financial_inclusion.models.db.user_model import User
from financial_inclusion.models.db.profile_model import Profile
from financial_inclusion.core.logging import logging

logger = logging.getLogger(__name__)

# CREATE operation
def create_user(db: Session,id:str,email:str,name:str,picture:str) -> User:

    """Creates a new user record."""
    user = User(
        id=id,
        email=email,
        name=name,
        picture=picture,
        has_completed_onboarding=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# READ operation
def get_user_by_id(db: Session,id: str) -> User| None:
    """Retrieves a user persona by their username."""
    return db.query(User).filter(User.id == id).first()


def get_user_profile_by_user_id(db: Session,user_id: str) -> dict| None:
    """Retrieves a users personal details by their user id."""
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    return profile._asdict() if profile else None

def create_user_profile(db: Session, user_id: str, personal_data: dict) -> Profile:
    """Creates a new user profile."""
    profile = Profile(
        user_id=user_id,
        personal_data=personal_data
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

# UPDATE operation
def update_user_info(db: Session,username: str, new_info: dict) -> User| None:
    """Updates the persona_info object for a given user."""
    user = get_user_by_username(db, username)
    if user:
        user.persona_info = new_info
        db.commit()
        db.refresh(user)
    return user

# DELETE operation
def delete_user(db: Session,username: str) -> bool:
    """Deletes a user record by their username."""
    user_to_delete = get_user_by_username(db, username)
    if user_to_delete:
        db.delete(user_to_delete)
        db.commit()
        return True
    return False
