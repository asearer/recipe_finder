from .database import engine, Base, SessionLocal
from . import models, crud, auth
import os

def init_db():
    Base.metadata.create_all(bind=engine)

def seed():
    db = SessionLocal()
    # create sample users
    if not crud.get_user_by_username(db, 'alice'):
        alice = crud.create_user(db, 'alice', auth.get_password_hash('password123'))
    if not crud.get_user_by_username(db, 'bob'):
        bob = crud.create_user(db, 'bob', auth.get_password_hash('password123'))

    # sample recipes
    recipes = [
        {
            'title': 'Tomato Pasta',
            'description': 'Quick tomato pasta with garlic and basil.',
            'image_url': '',
            'ingredients': ['tomato', 'pasta', 'garlic', 'basil', 'olive oil'],
            'owner': 'alice'
        },
        {
            'title': 'Avocado Toast',
            'description': 'Simple avocado toast with lemon and pepper.',
            'image_url': '',
            'ingredients': ['avocado', 'bread', 'lemon', 'salt', 'pepper'],
            'owner': 'bob'
        },
        {
            'title': 'Chicken Stir Fry',
            'description': 'Vegetables and chicken stir-fried with soy sauce.',
            'image_url': '',
            'ingredients': ['chicken', 'soy sauce', 'broccoli', 'carrot', 'garlic'],
            'owner': 'alice'
        }
    ]
    for r in recipes:
        owner = crud.get_user_by_username(db, r['owner'])
        existing = db.query(models.Recipe).filter(models.Recipe.title==r['title']).first()
        if not existing:
            crud.create_recipe(db, r['title'], r['description'], r['image_url'], r['ingredients'], owner.id if owner else None)
    db.close()

if __name__ == '__main__':
    init_db()
    seed()
    print('Seeded sample data into recipes.db')
