from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import schemas, crud, auth
from .database import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI-Powered Recipe Finder (Portfolio)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(authorization: str | None = Header(None), db: Session = Depends(get_db)):
    if authorization is None:
        return None
    try:
        scheme, _, token = authorization.partition(' ')
        if scheme.lower() != 'bearer':
            return None
        payload = auth.decode_access_token(token)
        if payload is None:
            return None
        username = payload.get('sub')
        if username is None:
            return None
        user = crud.get_user_by_username(db, username=username)
        return user
    except Exception:
        return None

@app.post('/signup', response_model=schemas.Token)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_username(db, user.username)
    if existing:
        raise HTTPException(status_code=400, detail='Username already taken')
    hashed = auth.get_password_hash(user.password)
    u = crud.create_user(db, user.username, hashed)
    token = auth.create_access_token({'sub': u.username})
    return {'access_token': token, 'token_type': 'bearer'}

@app.post('/login', response_model=schemas.Token)
def login(user: schemas.UserCreate, db: Session = Depends(get_db)):
    u = crud.get_user_by_username(db, user.username)
    if not u or not auth.verify_password(user.password, u.hashed_password):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    token = auth.create_access_token({'sub': u.username})
    return {'access_token': token, 'token_type': 'bearer'}

@app.post('/recipes', response_model=schemas.Recipe)
def create_recipe_endpoint(recipe_in: schemas.RecipeCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    owner_id = current_user.id if current_user else None
    recipe = crud.create_recipe(db, recipe_in.title, recipe_in.description, recipe_in.image_url, recipe_in.ingredients, owner_id)
    return recipe

@app.get('/recipes', response_model=list[schemas.Recipe])
def list_recipes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_recipes(db, skip, limit)

@app.get('/recipes/{recipe_id}', response_model=schemas.Recipe)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    r = crud.get_recipe(db, recipe_id)
    if not r:
        raise HTTPException(status_code=404, detail='Not found')
    return r

@app.put('/recipes/{recipe_id}', response_model=schemas.Recipe)
def update_recipe(recipe_id: int, recipe_in: schemas.RecipeCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    r = crud.get_recipe(db, recipe_id)
    if not r:
        raise HTTPException(status_code=404, detail='Not found')
    # simple owner check
    if r.owner_id and (not current_user or r.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail='Not allowed')
    updated = crud.update_recipe(db, r, recipe_in.title, recipe_in.description, recipe_in.image_url, recipe_in.ingredients)
    return updated

@app.delete('/recipes/{recipe_id}')
def delete_recipe(recipe_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    r = crud.get_recipe(db, recipe_id)
    if not r:
        raise HTTPException(status_code=404, detail='Not found')
    if r.owner_id and (not current_user or r.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail='Not allowed')
    crud.delete_recipe(db, r)
    return {'ok': True}

@app.get('/search', response_model=list[schemas.Recipe])
def search(q: str = '', db: Session = Depends(get_db)):
    # q is comma-separated list of ingredients
    names = [s.strip() for s in q.split(',') if s.strip()]
    return crud.search_recipes_by_ingredients(db, names)
