from sqlalchemy import Boolean, Column, String
from financial_inclusion.integrations.db import Base

class User(Base):
    """
    SQLAlchemy User Model.
    This table will store user information retrieved from Google and from the onboarding process.
    """
    __tablename__ = "users"

    # The 'sub' (subject) claim from Google's token, a unique identifier for the user.
    id = Column(String, primary_key=True, index=True)
    
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    picture = Column(String)
    
    # This flag tracks if the user has completed the initial onboarding.
    has_completed_onboarding = Column(Boolean, default=False)

    # Fields to be filled in from the onboarding questionnaire
    region = Column(String, nullable=True)
    age_group = Column(String, nullable=True)
    financial_literacy = Column(String, nullable=True)

    def __str__(self):
        return f"(id={self.id}, email={self.email}, name={self.name})"

