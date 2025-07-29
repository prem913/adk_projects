from fastapi import APIRouter
from fastapi import APIRouter, Depends, HTTPException  
from starlette.config import Config
from starlette.requests import Request
from starlette.responses import RedirectResponse, JSONResponse
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from urllib.parse import urlencode

from financial_inclusion.integrations.db import get_db
from financial_inclusion.models.db.user_model import User
from financial_inclusion.models.db.profile_model import Profile
from financial_inclusion.services.user_service import (
    create_user
)
from financial_inclusion.core.logging import logging
from financial_inclusion.core.security import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    SECRET_KEY,
    ALGORITHM,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/user")
config = Config('.env')
oauth = OAuth(config)

oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile', 'prompt': 'select_account'}
)

@router.get('/login')
async def login_via_google(request: Request):
    redirect_uri = request.url_for('auth_callback')
    google = oauth.google
    if not google:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    return await google.authorize_redirect(request, redirect_uri)


@router.get('/auth', name='auth_callback')
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    google = oauth.google
    if not google:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    token = await google.authorize_access_token(request)
    user_info = token.get("userinfo")
    if not user_info:
        raise HTTPException(status_code=400, detail="Could not fetch user info from Google")

    user = db.query(User).filter(User.id == user_info['sub']).first()
    if not user:
        logger.info("user doesn't exists")
        user = create_user(
            db = db,
            id=user_info['sub'],
            email=user_info['email'],
            name=user_info.get('name', ''),
            picture=user_info.get('picture', '')
        )

    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})

    frontend_url = "http://localhost:5173/auth/callback"
    params = {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }
    redirect_url = f"{frontend_url}?{urlencode(params)}"
    return RedirectResponse(url=redirect_url)

@router.post("/token/refresh")
async def refresh_access_token(request: Request, db: Session = Depends(get_db)):
    try:
        body = await request.json()
        refresh_token = body.get('refresh_token')
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
            
        new_access_token = create_access_token(data={"sub": user.id})
        return {"access_token": new_access_token, "token_type": "bearer"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@router.get("/")
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Example of a protected endpoint.
    The 'get_current_user' dependency handles all the auth.
    """
    return current_user

@router.get('/logout')
async def logout(request: Request):
    request.session.pop('user_id', None)
    return RedirectResponse(url='/login')


@router.post('/profile')
async def set_user_profile(personal_data : dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Endpoint to set the user's profile information.
    """

    profile = Profile(
        user_id=current_user.id,
        personal_data=personal_data
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)
    return JSONResponse(
        status_code=201,
        content={"message": "Profile created successfully", "profile": profile.personal_data}
    )