from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates") # Set the directory for Jinja2 templates and create an instance of Jinja2Templates

posts: list[dict] = [
    {
        "id": 1,
        "author": "Corey Schafer",
        "title": "FastAPI is Awesome!",
        "content": "This framework is really easy to use and is super fast.",
        "date_posted": "April 20, 2025",
    },
    {
        "id": 2,
        "author": "Jane Doe",
        "title": "Python is Great for Web Development!",
        "content": "Python is a great language for web development, and FastAPI makes it even better.",
        "date_posted": "April 21, 2025"
    },
    {
        "id": 3,
        "author": "Jide Cardoso",
        "title": "Writing Code is the best thing to do",
        "content": "With the advent of AI, writing code has become more efficient and enjoyable.",
        "date_posted": "March 1, 2026"
    }
]

@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
def home(request: Request):
    return templates.TemplateResponse(
        request, "home.html", {"posts": posts, "title": "TestHome"},
        )


@app.get("/posts/{post_id}", include_in_schema=False)
def post_page(request: Request, post_id: int):
    for post in posts:
        if post["id"] == post_id:
            return templates.TemplateResponse(
                request, "post.html", {"post": post, "title": post["title"]},
        )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


@app.get("/api/posts")
def get_posts():
    return posts

@app.get("/api/posts/{post_id}")
def get_post(post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            return post
    # post = next((post for post in posts if post.get("id") == post_id), "Post not found") # Alternative way to find the post using a generator expression and the next() function as a pythonic idiom
    # return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

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

