from fastapi import HTTPException, status #exceptions are used as error handler, like in express we use try/catch
from sqlalchemy.orm import Session
from models.user_schema import User
from models.tweet_schema import Tweet
import bcrypt 
print("bcrypt module location:", bcrypt.__file__)
print("Available attributes:", dir(bcrypt))
from datetime import timedelta
from middleware.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from cache.db_cache import get_from_cache, save_to_cache

# @desc create new account
# route POST /api/users/register
def create_user(user, db: Session):
    #Validates if a username already exists
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Validates if an email already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # hashes the password using bcrypt (good security practice)
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

    # creates a new user with the provided data
    new_user = User(
        username = user.username,
        email = user.email,
        password_hash = hashed_password.decode('utf-8'),
        display_name = user.display_name,
        bio = user.bio,
    )
    # Adds the user to the database and commits the transaction
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# @desc login user
# route POST /users/login
def login_user(user_credentials, db: Session):
    # find user by username
    db_user = db.query(User).filter(User.username == user_credentials.username).first()

    if not db_user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid username or password",
            headers = {"WWW-Authenticate": "Bearer"},
        )
    # Checks if the password matches using bcrypt
    # we need to encode the password from teh request to bytes and comapre with stored hash
    _is_password_correct = bcrypt.checkpw(
        user_credentials.password.encode('utf-8'), #UTF-8 is a character encoding that can represent virtually all characters in the Unicode standard
        db_user.password_hash.encode('utf-8')
    )

    if not _is_password_correct:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail= "invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # After success password validation, generate access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(db_user.id)},
        expires_delta=access_token_expires
    )
    
    # If authentication is successful, return user data (without password)
    return {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "display_name": db_user.display_name,
        "bio": db_user.bio,
        "access_token": access_token,
        "token_type": "bearer",
        "message": "login successful"
    }

# @desc logout user
# route POST /users/logout
def logout_user():
    return {
        "success": True,
        "message": "User logged out successfully"
    }

# @desc retrieve all accouts
# route GET /users
def getAll_users(db: Session):
    # Check cache first
    cache_key = "all_users"
    cached_result = get_from_cache(cache_key)
    
    # If found in cache, return it
    if cached_result is not None:
        print(f"DB Cache HIT: {cache_key}")
        return cached_result
    
    print(f"DB Cache MISS: {cache_key}")
    # Not in cache, query the database
    users = db.query(User).all()

    # Process the results
    user_list = []
    for user in users:
        user_list.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "display_name": user.display_name,
            "bio": user.bio
        })
    
    result = {
        "count": len(user_list),
        "users": user_list
    }
    
    # Save to cache
    save_to_cache(cache_key, result)
    
    return result

# @desc retrieve specific accout
# route GET /users/{user_id}
"""
    Retrieves a specific user by their ID.
    
    :param user_id: The ID of the user to retrieve
    :param db: SQLAlchemy database session
    :return: User details if found
    :raises HTTPException: If user not found
    """
def get_user_by_id(user_id: int, db: Session):
    # Use user ID in the cache key
    cache_key = f"user_{user_id}"
    cached_result = get_from_cache(cache_key)
    
    if cached_result is not None:
        print(f"DB Cache HIT: {cache_key}")
        return cached_result
    
    print(f"DB Cache MISS: {cache_key}")
    # Not in cache, get from database
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"User with ID {user_id} not found"
        )
    
    result = {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "display_name": user.display_name,
            "bio": user.bio,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
    }
    
    # Save to cache
    save_to_cache(cache_key, result)
    
    return result

# @desc delete your own account
# route DELETE /users/{user_id}
"""
    Deletes a user account by ID.
    
    :param user_id: The ID of the user to delete
    :param db: SQLAlchemy database session
    :param current_user: The currently authenticated user
    :return: Success message if deleted
    :raises HTTPException: If user not found or not authorized
    """
def delete_user_by_id(user_id: int, db: Session, current_user):
    # Check if user is deleting their own account
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own account"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    db.delete(user)
    db.commit()
    
    return {
        "message": f"User with ID {user_id} has been deleted"
    }

# @desc search for account
# route GET /users/search?q={query}
def search_user_by_username(username: str, db: Session):
    # Use username in the cache key
    cache_key = f"user_search_{username}"
    cached_result = get_from_cache(cache_key)
    
    if cached_result is not None:
        print(f"DB Cache HIT: {cache_key}")
        return cached_result
    
    print(f"DB Cache MISS: {cache_key}")
    # Not in cache, search in database
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with username {username} not found"
        )
    
    result = {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "display_name": user.display_name,
            "bio": user.bio,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "following": 0, 
            "followers": 0,
            "joinDate": user.created_at.strftime("%B %Y")
        }
    }
    
    # Save to cache
    save_to_cache(cache_key, result)
    
    return result

# @desc retrieve all tweets made by the user with the given user_id
# route GET /users/{userId}/tweets
def get_tweets_by_user(user_id: int, db: Session):
    # Use user ID in the cache key
    cache_key = f"user_tweets_{user_id}"
    cached_result = get_from_cache(cache_key)
    
    if cached_result is not None:
        print(f"DB Cache HIT: {cache_key}")
        return cached_result
    
    print(f"DB Cache MISS: {cache_key}")
    # Not in cache, get from database
    tweets = db.query(Tweet).filter(Tweet.user_id == user_id).all()
    result = {"tweets": tweets}
    
    # Save to cache
    save_to_cache(cache_key, result)
    
    return result