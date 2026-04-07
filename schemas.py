"""This module defines the Pydantic models (schemas) used for data validation and serialization in the FastAPI application."""
from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserBase(BaseModel):
    """Base model for a user, containing common fields.
    """
    username: str = Field(min_length=1, max_length=50, description="The username of the user")
    email: EmailStr = Field(max_length=120, description="The email address of the user")
    # todo: update email entry to ensure that it is an email entry (with the "@" a mandatory entry)

class UserCreate(UserBase):
    """Model for creating a new user.
    """
    # password: str = Field(min_length=6, max_length=128, description="The password of the user")
    pass

class UserResponse(UserBase):
    """Model for responding with user information.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="The unique identifier for the user")
    image_file: str | None = Field(description="The filename of the user's profile image")
    image_path: str = Field(description="The file path to the user's profile image")

# Just to note here, this class inherits from the UserBase class, 
# which means that in the response from a request to get user 
# information, the fields defined in UserBase (username and email) will
#  also be included in the response, along with the additional fields 
# defined in UserResponse (id, image_file, and image_path). 
# However, the email field should not be exposed in the response for
#  security reasons, so it would be better to remove it from the 
# UserResponse model or create a separate model for user responses that 
# does not include the email field. This will be addressed in the next 
# iteration of the code when we implement user authentication and 
# authorization, where we will create a UserPublicResponse model that 
# excludes sensitive information like email and password.


class PostBase(BaseModel):
    """Base model for a blog post, containing common fields.
    """
    title: str = Field(min_length=1, max_length=100, description="The title of the blog post")
    content: str = Field(min_length=1, description="The content of the blog post")

class PostCreate(PostBase):
    user_id: int = Field(
        description="The unique identifier of the user creating the post") 
    # This is a temporary field for testing purposes, as we will implement user authentication and authorization in the next iteration of the code, where we will get the user_id from the authenticated user instead of passing it in the request body.

class PostUpdate(BaseModel):
    """Model for updating an existing blog post.
    """
    title: str | None = Field(default=None, min_length=1, max_length=100, description="The title of the blog post")
    content: str | None = Field(default=None, min_length=1, description="The content of the blog post")

class PostResponse(PostBase):
    """This model is used for responses when retrieving blog posts, ensuring that all fields are included in the response.
    """
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(description="The unique identifier for the blog post")
    user_id: int = Field(description="The unique identifier of the user who created the post")
    date_posted: datetime = Field(description="The date the blog post was published")
    author: UserResponse = Field(description="The author of the blog post")
