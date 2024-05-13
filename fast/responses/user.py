from typing import Union
from datetime import datetime
from pydantic import EmailStr, BaseModel

from responses.base import BaseResponse


class UserResponse(BaseResponse):
    id: int
    name: str
    email: EmailStr
    created_at: Union[str, None, datetime] = None
    
    

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"

class GPTResponse(BaseResponse):
    name: str
