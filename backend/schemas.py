from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class IngredientBase(BaseModel):
    name: str

class IngredientCreate(IngredientBase):
    pass

class Ingredient(IngredientBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class RecipeBase(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None

class RecipeCreate(RecipeBase):
    ingredients: List[str] = []

class Recipe(RecipeBase):
    id: int
    ingredients: List[Ingredient] = []
    owner_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
