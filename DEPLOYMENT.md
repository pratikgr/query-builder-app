# Deployment Guide

## Production Deployment Checklist

### 1. Environment Configuration

#### Backend (.env)
```
DATABASE_URL=postgresql://user:password@host:port/dbname
SECRET_KEY=your-very-secure-secret-key-here
CORS_ORIGINS=https://yourdomain.com
DEBUG=False
```

#### Frontend (.env)
```
REACT_APP_API_URL=https://api.yourdomain.com/api
```

### 2. Database Setup

For PostgreSQL (recommended for production):

```bash
# Install PostgreSQL client
pip install psycopg2-binary

# Update DATABASE_URL in .env
# Run migrations
cd backend
python -m app.db.init_db
```

### 3. Backend Deployment

#### Option A: Using Gunicorn (Recommended)

```bash
# Install gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn app.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  -b 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

#### Option B: Using Docker

Create `Dockerfile` in backend directory:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
```

Build and run:
```bash
docker build -t query-builder-api .
docker run -p 8000:8000 --env-file .env query-builder-api
```

### 4. Frontend Deployment

#### Build for Production

```bash
cd frontend
npm run build
```

This creates a `build/` directory with optimized production files.

#### Option A: Serve with Nginx

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    root /path/to/frontend/build;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

#### Option B: Deploy to Vercel/Netlify

Both platforms support automatic React deployments:

**Vercel:**
```bash
npm install -g vercel
cd frontend
vercel
```

**Netlify:**
```bash
npm install -g netlify-cli
cd frontend
netlify deploy --prod
```

#### Option C: Using Docker

Create `Dockerfile` in frontend directory:

```dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 5. Cloud Platform Deployments

#### AWS (EC2 + RDS)

1. **RDS Database:**
   - Create PostgreSQL RDS instance
   - Note connection details for DATABASE_URL

2. **EC2 Backend:**
   - Launch EC2 instance (Ubuntu recommended)
   - Install Python and dependencies
   - Set up systemd service for gunicorn
   - Configure security groups (port 8000)

3. **S3 + CloudFront (Frontend):**
   - Upload build files to S3 bucket
   - Configure CloudFront distribution
   - Set up custom domain with Route 53

#### Google Cloud Platform

1. **Cloud SQL:** Create PostgreSQL instance
2. **Cloud Run:** Deploy containerized backend
3. **Firebase Hosting:** Deploy frontend

```bash
# Backend
gcloud run deploy query-builder-api --source .

# Frontend
firebase init
firebase deploy
```

#### Heroku

**Backend:**
```bash
cd backend
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
```

**Frontend:**
```bash
cd frontend
# Set API URL in build process
heroku create your-frontend-name
heroku buildpacks:set mars/create-react-app
git push heroku main
```

### 6. Environment Variables Management

Use environment-specific configurations:

- **Development:** `.env.development`
- **Staging:** `.env.staging`
- **Production:** `.env.production`

Never commit `.env` files to version control.

### 7. Security Best Practices

1. **Enable HTTPS:** Use Let's Encrypt or cloud provider SSL
2. **Set secure CORS origins:** Restrict to your domain only
3. **Use strong SECRET_KEY:** Generate with `openssl rand -hex 32`
4. **Implement rate limiting:** Use FastAPI middleware
5. **Add authentication:** Implement JWT or OAuth
6. **Database security:** Use read-only users where possible
7. **Input validation:** Already implemented via Pydantic
8. **SQL injection protection:** Using SQLAlchemy ORM (parameterized)

### 8. Monitoring and Logging

#### Backend Logging

Add to `main.py`:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

#### Application Monitoring

- **Sentry:** Error tracking
- **DataDog:** Performance monitoring
- **CloudWatch/Stackdriver:** Cloud-native monitoring

### 9. Backup Strategy

1. **Database backups:** Automated daily backups
2. **Code backups:** Git repository (GitHub/GitLab/Bitbucket)
3. **Media/uploads:** S3 versioning or similar

### 10. Performance Optimization

#### Backend:
- Enable database connection pooling
- Implement caching (Redis)
- Use CDN for static assets
- Optimize database queries (add indexes)

#### Frontend:
- Code splitting
- Lazy loading
- Image optimization
- Compression (gzip/brotli)

### 11. CI/CD Pipeline

Example GitHub Actions workflow:

```yaml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy Backend
        run: |
          # Deploy to your hosting
          
      - name: Deploy Frontend
        run: |
          cd frontend
          npm install
          npm run build
          # Deploy build folder
```

### 12. Health Checks

Both services include health check endpoints:

- Backend: `GET /health`
- Configure load balancer to use health checks
- Set up alerts for failed health checks

### 13. Scaling Considerations

- **Horizontal scaling:** Multiple backend instances behind load balancer
- **Database scaling:** Read replicas, connection pooling
- **Caching:** Redis for frequent queries
- **CDN:** CloudFront, Cloudflare for static assets

### 14. Cost Optimization

- Use auto-scaling groups
- Implement query result caching
- Use reserved instances for predictable workloads
- Monitor and optimize database queries
- Implement lazy loading for large datasets

## Quick Production Checklist

- [ ] Update all environment variables
- [ ] Change SECRET_KEY to secure random value
- [ ] Set DEBUG=False
- [ ] Configure production database
- [ ] Set CORS origins to production domain
- [ ] Build frontend with production API URL
- [ ] Enable HTTPS/SSL
- [ ] Set up monitoring and logging
- [ ] Configure automated backups
- [ ] Test all endpoints
- [ ] Set up CI/CD pipeline
- [ ] Configure domain and DNS
- [ ] Enable rate limiting
- [ ] Review security settings
- [ ] Test error handling
- [ ] Load testing

## Support

For issues during deployment, check:
1. Application logs
2. Database connectivity
3. CORS configuration
4. Environment variables
5. Network/firewall rules
