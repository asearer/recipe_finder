# AI-Powered Recipe Finder (Portfolio Project)

A full-stack web application for finding and managing recipes, built with FastAPI and vanilla JavaScript.

## 🚀 Features

- **User Authentication**: JWT-based signup and login system
- **Recipe Management**: Create, read, update, and delete recipes
- **Smart Search**: Find recipes by ingredients using comma-separated search
- **Image Support**: Add images to recipes via URL
- **Responsive Design**: Clean, mobile-friendly interface
- **RESTful API**: Well-documented FastAPI backend with automatic OpenAPI docs

## 🏗️ Tech Stack

**Backend:**
- FastAPI (Python web framework)
- SQLAlchemy 2.0 (ORM)
- SQLite (database)
- JWT authentication with python-jose
- Pydantic v2 (data validation)

**Frontend:**
- Vanilla HTML/CSS/JavaScript
- Fetch API for HTTP requests
- Responsive CSS Grid/Flexbox layout

## 📦 Quick Setup

### Option 1: Automated Setup (Recommended)

```bash
# Clone and navigate to the project
cd recipe_finder_portfolio

# Run the setup script
python3 setup.py

# Start both servers
python3 run.py
```

### Option 2: Manual Setup

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start backend server
uvicorn backend.main:app --reload --port 8000

# In another terminal, start frontend server
cd frontend
python3 -m http.server 3000
```

## 🌐 Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

## 📚 Usage

### 1. Authentication
- Sign up with a username and password
- Log in to receive a JWT token
- Token is automatically used for authenticated requests

### 2. Managing Recipes
- **Create**: Add new recipes with title, description, ingredients, and image URL
- **View**: Browse all recipes or search by specific ingredients
- **Update**: Edit your own recipes (ownership-based permissions)
- **Delete**: Remove recipes you've created

### 3. Search Functionality
- Enter comma-separated ingredients (e.g., "tomato, pasta, cheese")
- System finds recipes containing ALL specified ingredients
- Case-insensitive matching

## 🛠️ Development

### Project Structure
```
recipe_finder_portfolio/
├── backend/
│   ├── __init__.py
│   ├── main.py          # FastAPI app and routes
│   ├── models.py        # SQLAlchemy database models
│   ├── schemas.py       # Pydantic models for API
│   ├── database.py      # Database configuration
│   ├── auth.py          # JWT authentication logic
│   ├── crud.py          # Database operations
│   └── seed_data.py     # Sample data seeder
├── frontend/
│   ├── index.html       # Main HTML page
│   ├── app.js          # JavaScript application logic
│   └── styles.css      # CSS styling
├── requirements.txt     # Python dependencies
├── setup.py            # Automated setup script
├── run.py              # Development server runner
└── README.md           # This file
```

### Available Scripts

```bash
# Setup project
python3 setup.py

# Run both servers
python3 run.py

# Run only backend
python3 run.py backend

# Run only frontend
python3 run.py frontend

# Get help
python3 run.py help
```

### API Endpoints

**Authentication:**
- `POST /signup` - Create new user account
- `POST /login` - Login and receive JWT token

**Recipes:**
- `GET /recipes` - List all recipes (with pagination)
- `POST /recipes` - Create new recipe (requires auth)
- `GET /recipes/{id}` - Get specific recipe
- `PUT /recipes/{id}` - Update recipe (requires ownership)
- `DELETE /recipes/{id}` - Delete recipe (requires ownership)
- `GET /search?q=ingredients` - Search recipes by ingredients

## 🔧 Configuration

### Environment Variables (Optional)
Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./recipes.db
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

### Database
- Development uses SQLite (`recipes.db`)
- For production, update `DATABASE_URL` to PostgreSQL
- Database tables are created automatically on first run

## 📝 Notes

- **Security**: Change the `SECRET_KEY` in `backend/auth.py` for production
- **CORS**: Currently allows all origins for development
- **Images**: Currently uses URLs; consider cloud storage for production
- **Database**: SQLite is fine for development; use PostgreSQL for production
- **Error Handling**: Basic error responses; enhance for production use

## 🚀 Deployment Considerations

For production deployment:

1. **Environment**: Set proper environment variables
2. **Database**: Migrate to PostgreSQL or similar
3. **Security**: Implement proper CORS, rate limiting, HTTPS
4. **Images**: Use cloud storage (AWS S3, Cloudinary)
5. **Frontend**: Consider using a proper web server (nginx)
6. **Monitoring**: Add logging and monitoring tools
