from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from google.adk.cli.fast_api import get_fast_api_app
from financial_inclusion.api.v1.financial_coach_agent_api import router as financial_coach_agent_api
from financial_inclusion.api.v1.topic_api import router as topic_api
from financial_inclusion.api.v1.user_api import router as user_api
from financial_inclusion.core.settings import settings

from financial_inclusion.models.db.user_model import Base
from financial_inclusion.integrations.db import engine
from starlette.middleware.sessions import SessionMiddleware

Base.metadata.create_all(bind=engine)
origins = ["http://localhost:5173"]

app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRITPION,
    version=settings.VERSION,
)
app.add_middleware(SessionMiddleware, secret_key="!secret")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# router
app.include_router(router=user_api)
app.include_router(router=topic_api)
app.include_router(router=financial_coach_agent_api)


# adk_app = get_fast_api_app(agents_dir="src/financial_inclusion/agents", web=True)
# adk_app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# adk_app.routes.extend(app.routes)
#
# app.mount(path="", app=adk_app)

main_app = app

def get_openapi_with_custom_info():
    if main_app.openapi_schema:
        return main_app.openapi_schema
    openapi_schema = get_openapi(title=settings.APP_TITLE, version=settings.VERSION, description=settings.APP_DESCRITPION,summary="Api documentation for Financial Coach",routes=app.routes)
    main_app.openapi_schema = openapi_schema
    return main_app.openapi_schema

main_app.openapi = get_openapi_with_custom_info
