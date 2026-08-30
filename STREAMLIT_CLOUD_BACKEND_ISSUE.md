# Streamlit Cloud Backend Connectivity Issue & Solution

## Problem

When deploying SIF Sentinel to Streamlit Cloud, the frontend cannot reach the FastAPI backend running as a subprocess.

**Root Cause:**
- Streamlit Cloud runs the app in a container
- The backend subprocess runs on `localhost:8000` inside the container  
- The frontend (browser) runs on the USER'S machine
- The browser cannot access `localhost:8000` because it refers to the user's local machine, not the server

## Current Status

✅ **Local Development**: Works perfectly
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:8501` (Streamlit dev server)
- Direct communication works

❌ **Streamlit Cloud**: Frontend cannot reach backend
- Backend: Runs inside container on `localhost:8000`
- Frontend: Serves from `https://share.streamlit.io/...`
- Browser cannot access server's localhost

## Recommended Solutions

### Option 1: Deploy Backend to Separate Service (RECOMMENDED)

Deploy the FastAPI backend to a publicly accessible service:

#### A. Railway (Simplest)
1. Create Railway account: https://railway.app
2. Create new project → GitHub repo
3. Add `requirements.txt` from `/backend` folder
4. Set environment variables:
   - `MONGODB_URI`: Your MongoDB connection string
   - `JWT_SECRET`: Your JWT secret
   - `DEBUG`: `false`
5. Railway will generate a public URL: `https://yourapp-production.up.railway.app`
6. Update Streamlit Cloud secrets:
   - Add new secret: `BACKEND_API_URL = https://yourapp-production.up.railway.app`

#### B. Render.com
1. Create Render account: https://render.com
2. Create new "Web Service" → GitHub repo
3. Configure:
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && uvicorn main:app --host 0.0.0.0 --port 8000`
4. Get public URL and add to Streamlit Cloud secrets

#### C. Heroku (Free tier retired, but still possible with hobby dyno)
- Similar setup to Railway

### Option 2: Embed Backend in Streamlit App

Refactor the app to integrate FastAPI endpoints directly into Streamlit using:
- `st.selectbox`, `st.input`, etc. for frontend
- FastAPI routes called directly from Python
- More complex but keeps everything in one deployment

### Option 3: Use Streamlit Community Cloud Features

Streamlit Cloud doesn't natively support running multiple ports, but you could:
- Use a Streamlit component library to handle API proxying
- Not recommended - adds complexity

## Implementation Steps (Railway Recommended)

### Step 1: Deploy Backend to Railway

```bash
# Ensure backend/requirements.txt exists
# Commit all changes
git add .
git commit -m "Prepare for backend deployment"
git push

# Create new repo or use existing GitHub repo in Railway
```

### Step 2: Configure Environment Variables in Railway

In Railway dashboard:
```
MONGODB_URI=mongodb+srv://...your-connection-string...
JWT_SECRET=your-secret-key
DEBUG=false
CORS_ORIGINS=https://share.streamlit.io/*,https://localhost:8501
```

### Step 3: Update `backend/config.py`

Add support for external backend URL:
```python
FRONTEND_API_URL = os.getenv("FRONTEND_API_URL", "http://localhost:8000")
```

### Step 4: Modify `app.py` to Use External Backend

```python
# In app.py, change:
BACKEND_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")

# Update frontend configuration:
backend_url = BACKEND_URL if BACKEND_URL != "http://localhost:8000" else "http://localhost:8000/api"
html = html.replace("</head>", f"""
<script>
    window.API_CONFIG = {{ baseURL: '{backend_url}/api' }};
</script>
</head>""")
```

### Step 5: Update Streamlit Cloud Secrets

In Streamlit Cloud dashboard (`~/.streamlit/secrets.toml`):
```toml
BACKEND_API_URL = "https://your-railway-app.up.railway.app"
MONGODB_URI = "your-mongodb-connection"
JWT_SECRET = "your-jwt-secret"
```

### Step 6: Update Frontend API Configuration

Modify `frontend/src/services/api.js`:
```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 
                     (window.API_CONFIG?.baseURL) ||
                     '/api'
```

## Testing

### Local Testing
```bash
# Terminal 1: Start Streamlit
streamlit run app.py

# Terminal 2: Backend runs automatically
# Visit http://localhost:8501
# Try login with demo credentials
```

### Cloud Testing
1. Deploy backend to Railway/Render
2. Get public URL
3. Update Streamlit Cloud secrets with backend URL
4. Re-deploy Streamlit app
5. Test login functionality

## Demo Credentials

```
Email: admin@sif.com
Password: admin123

Email: officer@sif.com  
Password: officer123
```

## Architecture Diagram

### Local Development
```
Browser (localhost:8501)
    ↓
Streamlit (app.py)
    ├→ Backend subprocess (localhost:8000)
    └→ Frontend (React)
        ↓
    Backend API (localhost:8000)
```

### Streamlit Cloud (Recommended)
```
Browser (share.streamlit.io)
    ↓
Streamlit Cloud (app.py) ← Frontend served here
    ↓
Railway/Render ← Backend deployed here
    ↓
MongoDB Atlas
```

## Troubleshooting

### Issue: "Cannot reach the authentication server"
- Check if backend is deployed and running
- Verify `BACKEND_API_URL` in Streamlit Cloud secrets
- Check CORS configuration in backend allows Streamlit Cloud origin

### Issue: MongoDB connection fails
- Verify `MONGODB_URI` is correct and has network access from deployed service
- Check MongoDB Atlas network whitelist includes Railway/Render IPs

### Issue: CORS errors
- Add Streamlit Cloud domain to `CORS_ORIGINS` in backend secrets
- Add Railway/Render domain if using custom domains

## Files to Update

- [ ] `app.py` - Support external backend URL
- [ ] `backend/config.py` - Read backend URL from environment
- [ ] `frontend/src/services/api.js` - Use API config
- [ ] `.streamlit/secrets.toml` - Add backend URL and other secrets
- [ ] `railway.json` or `render.yaml` - Configure deployment

## Next Steps

1. Choose deployment option (Railway recommended)
2. Deploy backend to chosen service
3. Get public URL
4. Update environment variables
5. Test locally with external backend URL
6. Deploy to Streamlit Cloud
7. Test in production

## Additional Resources

- Railway: https://docs.railway.app
- Render: https://render.com/docs
- FastAPI CORS: https://fastapi.tiangolo.com/tutorial/cors/
- Streamlit Secrets: https://docs.streamlit.io/deploy/streamlit-cloud/deploy-your-app#secrets-management
