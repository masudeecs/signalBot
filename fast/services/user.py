from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import joinedload
from fastapi import HTTPException

from config.security import generate_token, get_token_payload, hash_password, \
    is_password_strong_enough, load_user, str_decode, str_encode, verify_password
from models.user import User, UserToken
from utils.string import unique_string
from config.settings import get_settings

settings = get_settings()

async def create_user_account(data, session):
    
    user_exist = session.query(User).filter(User.email == data.email).first()
    if user_exist:
        raise HTTPException(status_code=400, detail="Email is already exists.")
    
    if not is_password_strong_enough(data.password):
        raise HTTPException(status_code=400, detail="Please provide a strong password.")
    
    user = User()
    user.name = data.name
    user.email = data.email
    user.password = hash_password(data.password)
    user.updated_at = datetime.utcnow()
    session.add(user)
    session.commit()
    session.refresh(user)

    return user
    
async def get_login_token(data, session):
    # verify the email and password
    # generate access_token and refresh_token and ttl
    
    user = await load_user(data.username, session)
    if not user:
        raise HTTPException(status_code=400, detail="Email is not registered with us.")
    
    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect email or password.")
      
    # Generate the JWT Token
    return _generate_tokens(user, session)


async def get_refresh_token(refresh_token, session):
    token_payload = get_token_payload(refresh_token, settings.SECRET_KEY, settings.JWT_ALGORITHM)
    if not token_payload:
        raise HTTPException(status_code=400, detail="Invalid Request.")
    
    refresh_key = token_payload.get('t')
    access_key = token_payload.get('a')
    user_id = str_decode(token_payload.get('sub'))
    user_token = session.query(UserToken).options(joinedload(UserToken.user)).filter(UserToken.refresh_key == refresh_key,
                                                 UserToken.access_key == access_key,
                                                 UserToken.user_id == user_id,
                                                 UserToken.expires_at > datetime.utcnow()
                                                 ).first()
    if not user_token:
        raise HTTPException(status_code=400, detail="Invalid Request.")
    
    user_token.expires_at = datetime.utcnow()
    session.add(user_token)
    session.commit()
    return _generate_tokens(user_token.user, session)


def _generate_tokens(user, session):
    refresh_key = unique_string(100)
    access_key = unique_string(50)
    rt_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    user_token = UserToken()
    user_token.user_id = user.id
    user_token.refresh_key = refresh_key
    user_token.access_key = access_key
    user_token.expires_at = datetime.utcnow() + rt_expires
    session.add(user_token)
    session.commit()
    session.refresh(user_token)

    at_payload = {
        "sub": str_encode(str(user.id)),
        'a': access_key,
        'r': str_encode(str(user_token.id)),
        'n': str_encode(f"{user.name}")
    }

    at_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = generate_token(at_payload, settings.JWT_SECRET, settings.JWT_ALGORITHM, at_expires)

    rt_payload = {"sub": str_encode(str(user.id)), "t": refresh_key, 'a': access_key}
    refresh_token = generate_token(rt_payload, settings.SECRET_KEY, settings.JWT_ALGORITHM, rt_expires)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": at_expires.seconds
    }
 
async def fetch_user_detail(pk, session):
    user = session.query(User).filter(User.id == pk).first()
    if user:
        return user
    raise HTTPException(status_code=400, detail="User does not exists.")