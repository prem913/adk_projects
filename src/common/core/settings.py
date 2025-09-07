from pydantic_settings import BaseSettings
from dotenv import load_dotenv,find_dotenv

_ = load_dotenv(find_dotenv())

class Settings(BaseSettings):

    # FastAPI
    APP_TITLE: str = "ADK PROJECTS"
    APP_DESCRITPION: str = "A multi project project using ADK"
    VERSION: str = "1.0.0"
    GOOGLE_API_KEY: str="MY NOT SO PREMIUM API KEY"
    

    class Config:
        env_file :str= ".env"
        extra :str= "ignore"

settings = Settings()




