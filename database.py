from sqlalchemy import create_engine, Column, String, Boolean, ForeignKey,Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
import datetime
# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./user.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

# Define User model
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)

    posts = relationship("Post", back_populates="user")
  

# Define Post model
class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, index=True)
    content = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    user = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")
    images = relationship("Image", back_populates="post")


    @property
    def like_count(self):
        return len(self.likes)  # Count the number of likes for this post
    
# Define Comment model
class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"))  # Allow user_id to be nullable

    post = relationship("Post", back_populates="comments")
   

# Define Like model    
class Like(Base):
    __tablename__ = "likes"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    
    post = relationship("Post", back_populates="likes")

class Image(Base):
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)  # URL to store the image (can be a file path or a URL)
    post_id = Column(Integer, ForeignKey("posts.id"))
    
    post = relationship("Post", back_populates="images")   


    
