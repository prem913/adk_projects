from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from financial_inclusion.models.db.user_model import User
from financial_inclusion.integrations.db import Base
import json

# Define the UserPersona model
class Profile(Base):
    __tablename__ = 'profiles'

    user_id: Mapped[int] = mapped_column(primary_key=True)

    personal_data: Mapped[dict] = mapped_column(JSON)

    def __str__(self):
        return f"(id={self.id}, user_id={json.dumps(self.personal_data)})"