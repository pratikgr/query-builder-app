# Query Builder Application

A production-ready full-stack application featuring a dynamic query builder interface built with React Query Builder, FastAPI backend, and SQL database.

## Features

- 🔍 Interactive query builder with drag-and-drop support
- 💾 Save and load queries
- 🚀 Real-time query execution
- 📊 View query results in table format
- 🔄 Export queries to SQL format
- 🎨 Modern, responsive UI
- 🔒 API authentication ready
- 📝 Comprehensive error handling

## Tech Stack

### Frontend
- React 18
- TypeScript
- react-querybuilder
- Axios for API calls
- CSS Modules

### Backend
- FastAPI
- SQLAlchemy ORM
- Pydantic for validation
- SQLite (easily upgradable to PostgreSQL)
- CORS enabled

### Database
- SQLite with sample data
- Users and Products tables
- Migration support

## Project Structure

```
query-builder-app/
├── frontend/                 # React frontend application
│   ├── public/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API service layer
│   │   ├── types/          # TypeScript types
│   │   └── App.tsx         # Main app component
│   ├── package.json
│   └── tsconfig.json
├── backend/                 # FastAPI backend application
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core configurations
│   │   ├── db/             # Database models and setup
│   │   ├── schemas/        # Pydantic schemas
│   │   └── main.py         # FastAPI app entry
│   ├── requirements.txt
│   └── .env.example
└── README.md
```

## Installation & Setup

### Prerequisites
- Node.js 18+ and npm/yarn
- Python 3.9+
- pip

### Backend Setup

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

4. Create .env file:
```bash
cp .env.example .env
```

5. Initialize database:
```bash
python -m app.db.init_db
```

6. Run the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm start
```

The app will open at `http://localhost:3000`

## API Endpoints

### Query Management
- `POST /api/queries/execute` - Execute a query
- `POST /api/queries/save` - Save a query
- `GET /api/queries/` - List all saved queries
- `GET /api/queries/{id}` - Get a specific query
- `DELETE /api/queries/{id}` - Delete a query

### Metadata
- `GET /api/metadata/fields` - Get available fields for query builder
- `GET /api/metadata/tables` - Get database tables

## Usage

1. **Build a Query**: Use the visual query builder to create complex queries
   - Add rules and groups
   - Select fields, operators, and values
   - Combine with AND/OR logic

2. **Execute Query**: Click "Execute Query" to run against the database

3. **Save Query**: Give your query a name and save it for later use

4. **View Results**: Results display in a responsive table format

5. **Export**: View the generated SQL query

## Development

### Adding New Fields

Edit `backend/app/db/models.py` to add new database models, then update `backend/app/api/endpoints/metadata.py` to expose the fields.

### Customizing UI

Modify components in `frontend/src/components/` to customize the appearance and behavior.

### Database Migration

To switch to PostgreSQL:
1. Update `backend/app/core/config.py` with PostgreSQL connection string
2. Install psycopg2: `pip install psycopg2-binary`
3. Run migrations

## Production Deployment

### Backend
```bash
# Use gunicorn with uvicorn workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### Frontend
```bash
# Build for production
npm run build

# Serve with nginx or any static file server
```

### Environment Variables
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: JWT secret key
- `CORS_ORIGINS`: Allowed CORS origins

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Security Considerations

- Enable authentication for production
- Use HTTPS in production
- Validate and sanitize all inputs
- Implement rate limiting
- Use environment variables for secrets
- Enable SQL injection protection (parameterized queries)

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Support

For issues and questions, please open an issue on the repository.
