from pydantic_settings import BaseSettings
from dotenv import load_dotenv,find_dotenv

_ = load_dotenv(find_dotenv())

class Settings(BaseSettings):

    # FastAPI
    APP_TITLE: str = "AI Financial Coach API"
    APP_DESCRITPION: str = "Backend for the AI Financial Coach, providing personalized financial advice."
    VERSION: str = "1.0.0"

    class Config:
        env_file :str= ".env"
        extra :str= "ignore"

settings = Settings()




