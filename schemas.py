from pydantic import BaseModel
from typing import List,Optional

# Comment schemas
class CommentCreate(BaseModel):
    content: str
    post_id: int

    class Config:
        form_attributes = True


class CommentOut(BaseModel):
    id: int
    content: str  # Can be None if no user association
    post_id: int

    class Config:
        form_attributes = True


class LikeOut(BaseModel):
    id: int
    post_id: int

    class Config:
       form_attributes = True

# Image schemas
class ImageCreate(BaseModel):
    url: str  # The URL or path of the image


class ImageOut(ImageCreate):
    id: int  # Image ID will be automatically included in the response
    
    class Config:
        form_attributes = True # Tells Pydantic to treat the SQLAlchemy models like dictionaries


# Post schemas
class PostCreate(BaseModel):
    title: str
    content: str
    image: Optional[ImageCreate] = None 

class PostOut(BaseModel):
    id: int
    title: str
    content: str
    like_count: int
    comments: List[CommentOut] = []  # Include comments in the response
    images: List[ImageOut] = []  # Include images in the response
    
    class Config:
         form_attributes = True

# User schemas
class UserCreate(BaseModel):
    username: str
    password: str
    role: str

    class Config:
        form_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
