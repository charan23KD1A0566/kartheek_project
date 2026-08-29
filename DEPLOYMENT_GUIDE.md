# SIF Sentinel - Docker Deployment Guide

## 📋 Prerequisites

### Required
- Docker & Docker Compose installed
- MongoDB Atlas account (free tier available at https://www.mongodb.com/cloud/atlas)
- Git (for cloning)
- Domain name (for production)

### Optional
- Docker Hub account (for image registry)
- SSL certificate (for HTTPS)

---

## 🚀 Quick Start - Local Development

### 1. Clone the Project
```bash
git clone <your-repo>
cd sif-sentinel
```

### 2. Set Up Environment
```bash
# Copy example env and update
cp .env.production .env.local

# Edit with your values (keep defaults for local dev)
# nano .env.local
```

### 3. Run Locally (With Local MongoDB)
```bash
# Build images
docker compose build

# Run with local MongoDB
docker compose --profile local up -d

# Access:
# Frontend: http://localhost
# Backend API: http://localhost:8000
# MongoDB: localhost:27017
```

### 4. View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f mongodb
```

### 5. Stop Services
```bash
docker compose down
```

---

## 🌐 Production Deployment

### Step 1: Set Up MongoDB Atlas

1. Go to https://www.mongodb.com/cloud/atlas
2. Create free account or sign in
3. Create a cluster:
   - Click "Create a Database"
   - Choose "M0 Free" tier (sufficient for MVP)
   - Choose your region
   - Wait 3-5 minutes for cluster to be ready
4. Create database user:
   - Click "Database Access"
   - Add Database User
   - Create username & password (save these)
5. Get connection string:
   - Click "Clusters" → "Connect"
   - Choose "Connect your application"
   - Copy connection string: `mongodb+srv://username:password@cluster.mongodb.net/database`
6. Whitelist IP:
   - Click "Network Access"
   - Add IP Address: `0.0.0.0/0` (allows all IPs - use specific IPs in production)

### Step 2: Generate Secrets

```bash
# Generate secure JWT secret (run on your machine)
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 3: Prepare .env.production

```bash
# Copy the template
cp .env.production .env.prod

# Edit with your production values:
# - MongoDB Atlas connection string
# - JWT_SECRET from step 2
# - FRONTEND_API_URL: your production domain
# - DEBUG=False
```

### Step 4: Build Docker Images

```bash
# Build images
docker compose build

# Optionally tag and push to registry
docker tag sif-sentinel:latest yourusername/sif-sentinel:latest
docker push yourusername/sif-sentinel:latest
```

### Step 5: Deploy to Server

#### Option A: Direct Docker Compose (Simple VPS/Linux)

```bash
# Copy to server
scp -r . user@your-server:/home/user/sif-sentinel
ssh user@your-server

# Navigate to project
cd sif-sentinel

# Copy production env
cp .env.production .env

# Pull any images if using registry
docker compose pull

# Start services (without MongoDB - using Atlas)
docker compose up -d --no-build

# Verify all containers running
docker compose ps

# Check logs
docker compose logs -f backend
```

#### Option B: AWS ECS (Scalable)

1. Create ECR repositories for backend and frontend
2. Push images:
   ```bash
   docker tag sif-sentinel:latest <aws-account>.dkr.ecr.<region>.amazonaws.com/sif-sentinel:latest
   docker push <aws-account>.dkr.ecr.<region>.amazonaws.com/sif-sentinel:latest
   ```
3. Create ECS cluster
4. Create task definitions for backend and frontend
5. Create services in the cluster
6. Add Application Load Balancer for routing
7. Configure security groups and IAM roles

#### Option C: Digital Ocean App Platform

1. Connect GitHub repo to Digital Ocean
2. Create app.yaml:
   ```yaml
   name: sif-sentinel
   services:
   - name: backend
     github:
       repo: your-repo
       branch: main
     build_command: docker build -f Dockerfile -t backend .
     envs:
     - key: MONGODB_URI
       value: ${MONGODB_URI}
     - key: JWT_SECRET
       value: ${JWT_SECRET}
   ```
3. Deploy via DO dashboard

### Step 6: Set Up Reverse Proxy & SSL

Install Nginx and Certbot:
```bash
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx

# Configure Nginx to proxy to Docker
sudo nano /etc/nginx/sites-available/default
```

Nginx config:
```nginx
server {
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable SSL:
```bash
sudo certbot --nginx -d your-domain.com
# Certbot auto-renews certificates
```

### Step 7: Monitor & Maintain

```bash
# View all containers
docker compose ps

# View logs with timestamps
docker compose logs --timestamps

# Restart a service
docker compose restart backend

# View resource usage
docker stats

# Backup MongoDB Atlas data
# Use MongoDB Atlas Backup feature (automatic daily)

# Update application
git pull origin main
docker compose build
docker compose up -d
```

---

## 🛡️ Security Checklist

- [ ] JWT_SECRET is 32+ characters and random
- [ ] MongoDB Atlas has strong password
- [ ] Network access whitelisted to specific IPs (not 0.0.0.0 in production)
- [ ] HTTPS/SSL enabled
- [ ] DEBUG=False in production
- [ ] Firewall configured (only expose ports 80/443)
- [ ] Regular backups configured
- [ ] Rate limiting enabled on API
- [ ] CORS properly configured
- [ ] Secrets not committed to git (.env in .gitignore)

---

## 📊 Monitoring & Health Checks

All services have health checks configured:

```bash
# View health status
docker compose ps

# Test backend health
curl http://localhost:8000/api/health

# Test frontend
curl http://localhost/index.html

# View detailed status
docker inspect sif_sentinel_backend
```

---

## 🔧 Troubleshooting

### MongoDB Connection Failed
```bash
# Verify connection string
docker compose logs backend | grep MongoDB

# Test connection
docker exec sif_sentinel_backend python -c "
from pymongo import MongoClient
client = MongoClient('$MONGODB_URI')
print('Connected!' if client.admin.command('ping')['ok'] else 'Failed')
"
```

### Frontend can't reach API
```bash
# Check if backend is running
docker compose ps backend

# Test API endpoint
curl -i http://localhost:8000/api/health

# Check nginx logs
docker compose logs frontend
```

### Port already in use
```bash
# Find process using port
sudo lsof -i :8000

# Use different port in docker-compose.yml
# Change "8000:8000" to "8001:8000"
```

### Container won't start
```bash
# View startup logs
docker compose logs backend

# Check image built correctly
docker image ls | grep sif

# Rebuild without cache
docker compose build --no-cache
```

---

## 📈 Scaling & Performance

### Horizontal Scaling (Multiple backend instances)

```yaml
# In docker-compose.yml
backend:
  deploy:
    replicas: 3
  # Add load balancer in front
```

### Database Optimization
- Use MongoDB indexes on frequently queried fields
- Archive old reports to separate collection
- Enable compression in MongoDB Atlas

### Caching
- Add Redis cache layer between API and MongoDB
- Cache ML model predictions
- Cache taxonomy data

---

## 📞 Support & Documentation

- Backend API Docs: http://your-domain/docs (Swagger)
- Health endpoint: GET /api/health
- Status page: GET /api/status

For issues, check:
1. Container logs: `docker compose logs [service]`
2. Network connectivity: `docker network inspect sif_sentinel_network`
3. Volume mounts: `docker volume ls | grep sif`

---

## 📅 Maintenance Schedule

- **Daily**: Review alert logs
- **Weekly**: Check MongoDB backup status
- **Monthly**: Review performance metrics, update dependencies
- **Quarterly**: Security audit, penetration testing
- **Yearly**: Database cleanup, archive old reports

---

## 🎯 Next Steps

1. ✅ Set up MongoDB Atlas
2. ✅ Generate and secure JWT_SECRET
3. ✅ Build Docker images
4. ✅ Deploy to production server
5. ✅ Configure domain & SSL
6. ✅ Monitor first 48 hours closely
7. ✅ Set up automated backups
8. ✅ Implement monitoring (Datadog, New Relic, etc.)

---

**Last Updated**: 2026-08-29  
**Version**: 1.0 (Production Ready)
