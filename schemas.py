"""This module defines the Pydantic models (schemas) used for data validation and serialization in the FastAPI application."""
from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class PostBase(BaseModel):
    """Base model for a blog post, containing common fields.
    """
    author: str = Field(min_length=1, max_length=50, description="The name of the author of the blog post")
    title: str = Field(min_length=1, max_length=100, description="The title of the blog post")
    content: str = Field(min_length=1, description="The content of the blog post")

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    """This model is used for responses when retrieving blog posts, ensuring that all fields are included in the response.
    """
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(description="The unique identifier for the blog post")
    date_posted: str = Field(description="The date the blog post was published")
