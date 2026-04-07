import models
from database import Base, engine, get_db
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

from schemas import PostCreate, PostResponse, PostUpdate, UserCreate, UserResponse

from sqlalchemy import select
from sqlalchemy.orm import Session

from typing import Annotated

# First, create the database tables based on the models defined in
#  models.py. This will create the users and posts tables in the 
# database if they do not already exist. The Base.metadata.create_all() 
# function is used to create the tables, and it takes the engine as an 
# argument to connect to the database. This step is necessary to ensure 
# that the database schema is set up correctly before we start handling
#  requests in our FastAPI application.
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.mount("/media", StaticFiles(directory="media"), name="media")

templates = Jinja2Templates(directory="templates") # Set the directory for Jinja2 templates and create an instance of Jinja2Templates

# posts: list[dict] = [
#     {
#         "id": 1,
#         "author": "Corey Schafer",
#         "title": "FastAPI is Awesome!",
#         "content": "This framework is really easy to use and is super fast.",
#         "date_posted": "April 20, 2025",
#     },
#     {
#         "id": 2,
#         "author": "Jane Doe",
#         "title": "Python is Great for Web Development!",
#         "content": "Python is a great language for web development, and FastAPI makes it even better.",
#         "date_posted": "April 21, 2025"
#     },
#     {
#         "id": 3,
#         "author": "Jide Cardoso",
#         "title": "Writing Code is the best thing to do",
#         "content": "With the advent of AI, writing code has become more efficient and enjoyable.",
#         "date_posted": "March 1, 2026"
#     }
# ]

@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
def home(request: Request, db:Annotated[Session, Depends(get_db)]):
    """This method retrieves all posts from the database  and passes
     them as a template response for rendering the homepage"""
    result = db.execute(select(models.Post))
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request, "home.html", {"posts": posts, "title": "Home"},
        )


@app.get("/posts/{post_id}", include_in_schema=False)
def post_page(request: Request, post_id: int, db: Annotated[Session, Depends(get_db)]):
    """This method defines the html route for retrieving a post"""
    result = db.execute(select(models.Post) .where(models.Post.id == post_id))
    post = result.scalars().first()
    if post:
            title = post.title[:50]
            return templates.TemplateResponse(
                request, "post.html", {"post": post, "title": title},
        )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

# html version of viewing a user's post
@app.get("/users/{user_id}/posts", include_in_schema=False, name="user_posts")
def user_posts_page(request: Request, user_id: int, db: Annotated[Session, Depends(get_db)],):
    """ """
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
    posts = result.scalars().all()
    return  templates.TemplateResponse(
        request, "user_posts.html", {"posts": posts, "user": user, "title": f"{user.username}'s Posts"},
    )


@app.post("/api/users", response_model=UserResponse,
          status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.username == user.username))
    existing_user = result.scalar_one_or_none() # application-level 
    # constraint is used here in addition to the database-level 
    # constraint of unique=True in the User model to ensure that 
    # usernames are unique. This is done by querying the database for an
    #  existing user with the same username before attempting to create 
    # a new user. If an existing user is found, an HTTPException is 
    # raised with a 400 Bad Request status code and a message indicating 
    # that the username already exists. This helps to prevent duplicate 
    # usernames and maintain data integrity in the application.
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    
    result = db.execute(select(models.User).where(models.User.email == user.email))
    existing_user = result.scalar_one_or_none() 
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists") 
    
    new_user = models.User(
        username=user.username,
        email=user.email
    )

    db.add(new_user) # The new user is added to the database session using db.add(new_user). This tells SQLAlchemy that we want to insert a new record into the users table with the data provided in the new_user object. However, at this point, the new user is not yet saved to the database. To actually save the new user to the database, we need to call db.commit(), which will commit the transaction and persist the changes to the database. After committing, we can call db.refresh(new_user) to refresh the new_user object with any changes that were made during the commit, such as automatically generated fields like the id. Finally, we return the new_user object, which will be serialized and sent back in the response according to the UserResponse schema.
    db.commit() # Commits the transaction to save the new user to the database
    db.refresh(new_user) # Refreshes the new_user object with any changes made during the commit, such as automatically generated fields like the id
    return new_user

@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int,  db: Annotated[Session, Depends(get_db)]):
    """Defines retriving a user by the user id"""
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@app.get("/api/users/{user_id}/posts", response_model=list[PostResponse])
def get_user_posts(
    user_id: int, db: Annotated[Session, Depends(get_db)]):
    """Defines function to get all posts associated with one user"""
    # Check if user exists first
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalar_one_or_none
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
    posts = result.scalars().all()
    return posts


@app.get("/api/posts", response_model=list[PostResponse])
def get_all_posts(db: Annotated[Session, Depends(get_db)]):
    """Retrieves all post from the database for the api """
    result = db.execute(select(models.Post))
    posts = result.scalars().all()
    return posts

@app.post("/api/posts", response_model=PostResponse,
          status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == post.user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    new_post = models.Post(
        title=post.title,
        content=post.content,
        user_id=post.user_id,
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if post:
        return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.put("/api/posts/{post_id}", response_model=PostResponse)
def update_post_full(
    post_id: int, post_data: PostCreate, db: Annotated[Session, Depends(get_db)]
    ):
    """This method defines the function to update a post by its id, and 
    it expects the full post data in the request body. It first checks
    if the post exists, and if not, it raises a 404 Not Found error.
    Then it checks if the user_id in the post_data matches the user_id 
    of the existing post. If they do not match, it checks if the user 
    with the user_id in post_data exists. If the user does not exist, it 
    raises a 404 Not Found error. Finally, it updates the post's title, 
    content, and user_id with the new data from post_data, commits the 
    changes to the database, refreshes the post object to get any 
    updated fields, and returns the updated post.
    """
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    # Check if the user_id in post_data matches the user_id of the existing post. Will create authentication and authorization logic in the next iteration of the code to ensure that only the author of the post can update it, but for now, we will just check if the user_id in post_data exists in the database before allowing the update to proceed.
    if post_data.user_id != post.user_id:
        result = db.execute(select(models.User).where(models.User.id == post.user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    post.title = post_data.title
    post.content = post_data.content
    post.user_id = post_data.user_id
    db.commit()
    db.refresh(post)
    return post

@app.patch("/api/posts/{post_id}", response_model=PostResponse)
def update_post_partial(
    post_id: int, post_data: PostUpdate, db: Annotated[Session, Depends(get_db)]
    ):
    """ This method defines the function to update a post by its id, and
    it expects partial post data in the request body. It first checks if
    the post exists, and if not, it raises a 404 Not Found error. Then 
    it uses the model_dump() method of the Pydantic model to create a 
    dictionary of the fields that were explicitly set in the request 
    body, excluding any fields that were not included. It then iterates
    over the update_data dictionary and uses setattr() to update the 
    corresponding attributes of the post object with the new values. 
    Finally, it commits the changes to the database, refreshes the post
    object to get any updated fields, and returns the updated post.
    """
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    update_data = post_data.model_dump(exclude_unset=True)
    # exclude_unset=True tells Pydantic to only include fields that were explicitly set in the request, and to exclude any fields that were not included in the request. This allows for partial updates, where only the fields that need to be updated are included in the request body, and any fields that are not included will remain unchanged in the database.

    for key, value in update_data.items():
        setattr(post, key, value)

    db.commit()
    db.refresh(post)
    return post

@app.delete("/api/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Annotated[Session, Depends(get_db)]):
    """This method defines the function to delete a post by its id. It first checks if the post exists, and if not, it raises a 404 Not Found error. If the post exists, it deletes the post from the database and commits the transaction. Since the status code for this endpoint is 204 No Content, we do not return any content in the response after successfully deleting the post."""
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    db.delete(post)
    db.commit()
    # To do: add authentication and authorization logic to ensure that
    #  only the author of the post can delete it, but for now, we will 
    # just check if the post exists before allowing the delete to 
    # proceed. If the post does not exist, we raise a 404 Not Found 
    # error. If the post exists, we delete it from the database and 
    # commit the transaction. Since the status code for this endpoint is 
    # 204 No Content, we do not return any content in the response after
    # successfully deleting the post.

# Custom exception handler for HTTP exceptions
@app.exception_handler(StarletteHTTPException)
def http_exception_handler(request: Request, exc: StarletteHTTPException):
    message = (
        exc.detail 
        if exc.detail 
        else "An error occurred. Please check your request and try again.")
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": message},
        )
    return templates.TemplateResponse(
        request, "error.html", {"status_code": exc.status_code, "message": message, "title": f"{exc.status_code} Error"},
        status_code=exc.status_code,
    )

# Custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exc.errors()},
        )
    
    return templates.TemplateResponse(
        request, "error.html", {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid input. Please check your data and try again.",
            "title": "Validation Error"},
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )

