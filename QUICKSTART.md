# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Python 3.9 or higher
- Node.js 18 or higher
- npm or yarn

### Option 1: Automated Setup (Recommended)

#### Linux/Mac:
```bash
chmod +x start.sh
./start.sh
```

#### Windows:
```bash
start.bat
```

This will automatically:
- Set up virtual environment
- Install all dependencies
- Initialize database with sample data
- Start both backend and frontend servers

### Option 2: Manual Setup

#### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create environment file:
```bash
cp .env.example .env
```

5. Initialize database:
```bash
python -m app.db.init_db
```

6. Start the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000
API docs at: http://localhost:8000/docs

#### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create environment file:
```bash
cp .env.example .env
```

4. Start development server:
```bash
npm start
```

Frontend will open at: http://localhost:3000

## 📖 Using the Application

### Building Your First Query

1. **Select a Table**: Choose from Users, Products, or Orders
2. **Add Rules**: Click "+ Rule" to add filter conditions
3. **Set Conditions**: 
   - Select a field (e.g., "Age")
   - Choose an operator (e.g., ">")
   - Enter a value (e.g., "25")
4. **Add Groups**: Click "+ Group" for complex AND/OR logic
5. **Execute**: Click "Execute Query" to see results

### Saving Queries

1. Build your query
2. Click "Save Query"
3. Enter a name and description
4. Query is saved for later use

### Viewing Saved Queries

1. Click "Saved Queries" tab
2. Browse your saved queries
3. Click "Load" to reuse a query
4. Click "Delete" to remove a query

## 🎯 Example Queries

### Example 1: Active Users Over 25
- Table: Users
- Rule: age > 25
- Rule: is_active = true
- Combinator: AND

### Example 2: Electronics or Furniture Under $500
- Table: Products
- Group 1 (OR):
  - Rule: category = Electronics
  - Rule: category = Furniture
- Group 2:
  - Rule: price < 500
- Top Combinator: AND

### Example 3: Pending Orders with High Total
- Table: Orders
- Rule: status = pending
- Rule: total_amount > 1000
- Combinator: AND

## 🔧 Configuration

### Backend (.env)
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: Secret key for security
- `CORS_ORIGINS`: Allowed frontend origins
- `DEBUG`: Enable/disable debug mode

### Frontend (.env)
- `REACT_APP_API_URL`: Backend API URL

## 📊 Sample Data

The database is pre-populated with:
- 10 Users (various ages and locations)
- 10 Products (Electronics and Furniture categories)
- 20 Orders (various statuses and amounts)

## 🐛 Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.9+)
- Ensure virtual environment is activated
- Check if port 8000 is available

### Frontend won't start
- Check Node version: `node --version` (need 18+)
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`
- Check if port 3000 is available

### Database errors
- Delete query_builder.db and run `python -m app.db.init_db` again
- Check database permissions

### CORS errors
- Ensure backend CORS_ORIGINS includes frontend URL
- Check that backend is running
- Verify API URL in frontend .env

## 📚 API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔐 Security Notes

**For Development Only:**
- Default SECRET_KEY is insecure
- SQLite database for simplicity
- CORS allows localhost

**For Production:**
- See DEPLOYMENT.md for production setup
- Change SECRET_KEY
- Use PostgreSQL
- Configure proper CORS origins
- Enable HTTPS

## 🎓 Next Steps

1. Explore the API documentation
2. Try building complex queries
3. Examine the code structure
4. Customize fields and operators
5. Add your own tables/models
6. Deploy to production (see DEPLOYMENT.md)

## 💡 Tips

- Use keyboard shortcuts in the query builder
- Click on the SQL preview to see generated queries
- Results are limited to 100 rows by default
- Saved queries persist in the database
- The app uses SQLAlchemy ORM for SQL safety

## 🤝 Need Help?

- Check the README.md for detailed information
- Review API docs at /docs endpoint
- Examine code comments
- Check DEPLOYMENT.md for production guidance

Enjoy building queries! 🎉
