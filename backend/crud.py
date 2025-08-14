from sqlalchemy.orm import Session
from . import models

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, username: str, hashed_password: str):
    user = models.User(username=username, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_or_get_ingredient(db: Session, name: str):
    name = name.strip().lower()
    ingredient = db.query(models.Ingredient).filter(models.Ingredient.name == name).first()
    if not ingredient:
        ingredient = models.Ingredient(name=name)
        db.add(ingredient)
        db.commit()
        db.refresh(ingredient)
    return ingredient

def create_recipe(db: Session, title: str, description: str | None, image_url: str | None, ingredient_names: list, owner_id: int | None):
    recipe = models.Recipe(title=title, description=description, image_url=image_url, owner_id=owner_id)
    db.add(recipe)
    db.commit()
    for name in ingredient_names:
        ing = create_or_get_ingredient(db, name)
        recipe.ingredients.append(ing)
    db.commit()
    db.refresh(recipe)
    return recipe

def get_recipe(db: Session, recipe_id: int):
    return db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()

def list_recipes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Recipe).offset(skip).limit(limit).all()

def search_recipes_by_ingredients(db: Session, ingredient_list: list):
    # naive implementation: recipes that contain ALL specified ingredient names (case-insensitive)
    names = [n.strip().lower() for n in ingredient_list if n.strip()]
    if not names:
        return []
    q = db.query(models.Recipe)
    for name in names:
        q = q.filter(models.Recipe.ingredients.any(models.Ingredient.name == name))
    return q.all()

def update_recipe(db: Session, recipe: models.Recipe, title: str | None, description: str | None, image_url: str | None, ingredient_names: list | None):
    if title is not None:
        recipe.title = title
    if description is not None:
        recipe.description = description
    if image_url is not None:
        recipe.image_url = image_url
    if ingredient_names is not None:
        # replace ingredient list
        recipe.ingredients = []
        for name in ingredient_names:
            ing = create_or_get_ingredient(db, name)
            recipe.ingredients.append(ing)
    db.commit()
    db.refresh(recipe)
    return recipe

def delete_recipe(db: Session, recipe: models.Recipe):
    db.delete(recipe)
    db.commit()
