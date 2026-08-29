# 📋 Deployment Quick Reference Card

## 🚀 START HERE - 3 Minute Deployment Summary

### Prerequisites
- Docker installed
- MongoDB Atlas account (free: mongodb.com/cloud/atlas)
- Domain name (optional, localhost works locally)

### 3-Step Deployment

#### Step 1: Get MongoDB Connection String (MongoDB Atlas)
```
1. Create cluster at mongodb.com/cloud/atlas
2. Create database user  
3. Copy connection string
4. Format: mongodb+srv://user:pass@cluster.mongodb.net/sif_sentinel
```

#### Step 2: Create .env.production
```bash
# Windows Notepad or Linux nano
MONGODB_URI=mongodb+srv://user:pass@your-cluster.mongodb.net/sif_sentinel?retryWrites=true
MONGODB_DATABASE=sif_sentinel
JWT_SECRET=<generate: python -c "import secrets; print(secrets.token_urlsafe(32))">
FRONTEND_API_URL=http://localhost  # or your domain
DEBUG=False
```

#### Step 3: Deploy
```bash
# Build
docker compose build

# Run
docker compose up -d

# Verify (wait 10 seconds first)
docker compose ps
curl http://localhost:8000/api/health

# Open browser
http://localhost         # Frontend
http://localhost:8000/docs  # API docs
```

---

## 🆘 Emergency Commands

| Problem | Solution |
|---------|----------|
| Can't start containers | `docker compose down` then `docker compose up -d` |
| Port 8000 in use | Change in docker-compose.yml: `"8001:8000"` |
| Need logs | `docker compose logs -f backend` |
| MongoDB connection error | Check connection string, verify network access in Atlas |
| Frontend shows error | Check browser console (F12), check backend logs |
| Need to restart | `docker compose restart` |
| Emergency shutdown | `docker compose down` |

---

## 📊 What's Deployed

```
┌─ Frontend (React)      → Port 80
├─ Backend API (FastAPI) → Port 8000  
├─ MongoDB              → Atlas (cloud) or localhost:27017
└─ Nginx (proxy)        → Reverse proxy for APIs
```

---

## ✅ Verify Deployment Works

```bash
# Health check
curl http://localhost:8000/api/health

# Should return:
# {"status":"healthy","database":"connected"}

# Login test
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"employee@sifsentinel.demo","password":"Employee@123"}'

# Should return JWT token if working
```

---

## 🔑 Demo Credentials

```
Admin:        admin@sifsentinel.demo       / Admin@123
Manager:      manager@sifsentinel.demo     / Manager@123  
Safety:       safety@sifsentinel.demo      / Safety@123
Employee:     employee@sifsentinel.demo    / Employee@123
```

---

## 📁 Key Files for Deployment

```
Dockerfile              → Backend container definition
frontend.Dockerfile    → Frontend container definition
docker-compose.yml     → Orchestration configuration
nginx.conf             → Web server configuration
.env.production        → Production secrets (never commit!)
deploy.sh / deploy.bat → Deployment automation scripts
DEPLOYMENT_GUIDE.md    → Detailed instructions
PRE_DEPLOYMENT_CHECKLIST.md → Pre-launch verification
```

---

## 🌐 Access Points

| Component | URL |
|-----------|-----|
| Frontend | http://localhost or https://your-domain |
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Health | http://localhost:8000/api/health |

---

## ⚙️ Environment Variables Explained

| Variable | Purpose | Example |
|----------|---------|---------|
| `MONGODB_URI` | Database connection | `mongodb+srv://user:pass@cluster.mongodb.net/db` |
| `MONGODB_DATABASE` | Database name | `sif_sentinel` |
| `JWT_SECRET` | Auth signing key | Random 32+ chars |
| `FRONTEND_API_URL` | API base URL for frontend | `http://localhost` or domain |
| `DEBUG` | Debug mode (dev/prod) | `False` for production |
| `SERVER_HOST` | API listen address | `0.0.0.0` |
| `SERVER_PORT` | API listen port | `8000` |

---

## 🔒 Security Checklist (Pre-Production)

- [ ] JWT_SECRET is random (32+ chars)
- [ ] `.env.production` NOT in git
- [ ] DEBUG=False
- [ ] MongoDB password is strong
- [ ] MongoDB network access configured
- [ ] HTTPS/SSL enabled (after domain setup)
- [ ] Firewall configured (only 80, 443)
- [ ] Secrets never logged

---

## 📈 Performance Tips

1. **Enable Caching**: Nginx gzip compression ✅ (included in nginx.conf)
2. **Database Indexes**: MongoDB Atlas handles automatically
3. **CDN**: Add CloudFlare for static assets (optional)
4. **Monitoring**: Set up metrics dashboards (recommended)
5. **Scaling**: Load balancer + multiple backend instances (if needed)

---

## 🐛 Debugging

### Check Service Status
```bash
docker compose ps
# Shows all containers and their status
```

### View Logs
```bash
# All services
docker compose logs

# Specific service  
docker compose logs backend
docker compose logs frontend
docker compose logs mongodb

# Follow live logs
docker compose logs -f backend
```

### Test Database Connection
```bash
docker exec sif_sentinel_backend python -c "
from pymongo import MongoClient
import os
uri = os.getenv('MONGODB_URI')
client = MongoClient(uri)
print('✓ Connected!' if client.admin.command('ping')['ok'] else '✗ Failed')
"
```

### Test API Health
```bash
curl -v http://localhost:8000/api/health
```

---

## 💾 Backup & Recovery

### Local MongoDB
```bash
# Backup
docker exec sif_sentinel_mongodb mongodump --out /backup

# Restore  
docker exec sif_sentinel_mongodb mongorestore /backup
```

### MongoDB Atlas
```
MongoDB Atlas handles automatic daily backups
No manual action needed
Access backups in Atlas dashboard
```

---

## 🔄 Update & Maintenance

### Update Application
```bash
# Get latest code
git pull origin main

# Rebuild images
docker compose build

# Restart services
docker compose up -d
```

### Update Dependencies
```bash
# Backend
pip install -r backend/requirements.txt --upgrade

# Frontend
cd frontend && npm update

# Rebuild and redeploy
docker compose build
docker compose up -d
```

---

## 📞 Support Resources

1. **Deployment Issues** → See DEPLOYMENT_GUIDE.md
2. **Verification Checklist** → See PRE_DEPLOYMENT_CHECKLIST.md
3. **Architecture Details** → See ARCHITECTURE.md
4. **API Documentation** → http://localhost:8000/docs
5. **Container Logs** → `docker compose logs [service]`

---

## ✨ Deployment Profiles

### Local Development
```bash
docker compose --profile local up -d
# Includes local MongoDB
```

### Production (Atlas)
```bash
docker compose up -d
# Uses MongoDB Atlas (no local DB)
```

---

## 🎯 Recommended Next Steps

1. ✅ Set up MongoDB Atlas account
2. ✅ Generate JWT_SECRET
3. ✅ Create .env.production file
4. ✅ Run `docker compose build`
5. ✅ Run `docker compose up -d`
6. ✅ Test all endpoints
7. ✅ Set up SSL/domain
8. ✅ Configure monitoring
9. ✅ Create admin account
10. ✅ Train team & launch

---

## 📊 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Docker | 20.10+ | Latest |
| Docker Compose | 1.29+ | Latest |
| CPU | 1 core | 2+ cores |
| RAM | 2GB | 4GB+ |
| Disk | 10GB | 50GB+ |
| Network | 1 Mbps | 10 Mbps |

---

## 🚨 Critical Values

```
JWT Secret: Keep safe, never share
MongoDB Password: Keep safe, never share
API Keys: If added, keep in .env only
Secrets: NEVER commit to git
Backups: Store securely, test restore
```

---

## 📅 Maintenance Schedule

| Frequency | Task |
|-----------|------|
| Daily | Check error logs |
| Weekly | Verify backups |
| Monthly | Review performance |
| Quarterly | Security audit |
| Yearly | Full system review |

---

**Last Updated**: 2026-08-29  
**Version**: 1.0  
**Status**: 🟢 Production Ready  
**Time to Deploy**: ~15 minutes

---

**Questions?** Check DEPLOYMENT_GUIDE.md or PRE_DEPLOYMENT_CHECKLIST.md
