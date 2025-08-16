from typing import List, Optional
from pydantic import BaseModel, ConfigDict, field_validator


class IngredientBase(BaseModel):
    name: str
    
    @field_validator('name')
    @classmethod
    def validate_name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()


class IngredientCreate(IngredientBase):
    pass


class Ingredient(IngredientBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class RecipeBase(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    
    @field_validator('title')
    @classmethod
    def validate_title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()


class RecipeCreate(RecipeBase):
    ingredients: List[str] = []


class Recipe(RecipeBase):
    id: int
    ingredients: List[Ingredient]
    owner_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str
    password: str
    
    @field_validator('username')
    @classmethod
    def validate_username_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Username cannot be empty')
        return v.strip()
    
    @field_validator('password')
    @classmethod
    def validate_password_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Password cannot be empty')
        return v.strip()


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
