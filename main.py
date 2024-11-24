from fastapi import FastAPI, Depends, HTTPException, Query,status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import List, Optional
from datetime import timedelta
from database import engine, Base, SessionLocal, User, Post, Comment, Like,Image
from schemas import PostCreate, PostOut, CommentCreate, CommentOut, LikeOut, UserCreate, Token ,ImageCreate,ImageOut
from auth import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user,OAuth2PasswordRequestForm

# FastAPI app
app = FastAPI()

# Database initialization (recreate tables at startup)
@app.on_event("startup")
def startup():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Register new user
@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "User registered successfully"}

# Login and generate token
@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# Create new post
@app.post("/posts/", response_model=PostOut)
def create_post(post: PostCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Create new post
    new_post = Post(title=post.title, content=post.content, user_id=current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    # Handle image upload if provided
    if post.image:
        new_image = Image(url=post.image.url, post_id=new_post.id)
        db.add(new_image)
        db.commit()
        db.refresh(new_image)
    
    return new_post
# Get all posts with like count and comments (with search, filter, and pagination)
@app.get("/posts/", response_model=List[PostOut])
def read_posts(
    title: Optional[str] = None,  # Filter by title
    content: Optional[str] = None,  # Filter by content
    user_id: Optional[int] = None,  # Filter by user (author)
    skip: int = 0,  # Pagination: offset
    limit: int = 10,  # Pagination: max results per page
    db: Session = Depends(get_db)
):
    query = db.query(Post).options(joinedload(Post.likes), joinedload(Post.comments),joinedload(Post.images))

    # Apply title filter if provided
    if title:
        query = query.filter(Post.title.ilike(f"%{title}%"))
    
    # Apply content filter if provided
    if content:
        query = query.filter(Post.content.ilike(f"%{content}%"))

    # Apply filter by user_id (if provided)
    if user_id:
        query = query.filter(Post.user_id == user_id)

    # Apply pagination
    posts = query.offset(skip).limit(limit).all()

    return posts


# Create a comment on a post
@app.post("/comments/{post_id}", response_model=CommentOut)
def create_comment(post_id: int, comment: CommentCreate, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Create the comment without user_id
    new_comment = Comment(content=comment.content, post_id=post_id)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment

# Like a post (no authentication required)
@app.post("/likes/{post_id}")
def like_post(post_id: int, db: Session = Depends(get_db)):
    # Fetch the post
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Check if the post already has a like (you can skip this if multiple likes are allowed)
    db_like = db.query(Like).filter(Like.post_id == post_id).first()
    if db_like:
        raise HTTPException(status_code=400, detail="This post has already been liked")

    # Create the like (without user_id, making it public)
    new_like = Like(post_id=post_id)
    db.add(new_like)
    db.commit()
    db.refresh(new_like)

    return {"msg": "Post liked successfully"}


# Unlike a post
@app.delete("/likes/{post_id}")
def unlike_post(post_id: int, db: Session = Depends(get_db)):
    db_like = db.query(Like).filter(Like.post_id == post_id).first()
    if not db_like:
        raise HTTPException(status_code=404, detail="Like not found")
    
    db.delete(db_like)
    db.commit()
    return {"msg": "Like removed"}

# Get all likes for a post
@app.get("/likes/{post_id}", response_model=List[LikeOut])
def get_likes(post_id: int, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Return all likes for the post
    return db_post.likes
