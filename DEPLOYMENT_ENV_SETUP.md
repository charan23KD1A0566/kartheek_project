# Deployment Environment Configuration

## Overview
The app requires certain environment variables to be configured in your deployment platform. The `.env` file is not included in the repository, so you must set these variables through your deployment platform's UI or configuration.

## Required Environment Variables

### 1. **MONGODB_URI** (Required)
The connection string to your MongoDB database.

**For Local Development:**
```
MONGODB_URI=mongodb://localhost:27017/
```

**For MongoDB Atlas (Cloud):**
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/sif_sentinel?retryWrites=true&w=majority
```

⚠️ **CRITICAL**: If this is not set, the app will use `localhost:27017` which won't work in cloud deployments!

### 2. **MONGODB_DATABASE** (Optional)
The name of your MongoDB database. Defaults to `sif_sentinel`.

```
MONGODB_DATABASE=sif_sentinel
```

### 3. **JWT_SECRET** (Optional)
Secret key for JWT token signing. If not set, the app uses a default demo key `dev-jwt-secret-change-me`.

For production, generate a secure random key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Then set:
```
JWT_SECRET=<your-generated-secret>
```

### 4. **CORS_ORIGINS** (Optional)
Comma-separated list of allowed origins for CORS. Defaults to localhost addresses.

```
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 5. **FRONTEND_API_URL** (Optional)
Base URL for frontend API calls. Defaults to `http://localhost:5173`.

```
FRONTEND_API_URL=https://yourdomain.com/api
```

### 6. **DEBUG** (Optional)
Enable debug mode. Set to `False` for production.

```
DEBUG=False
```

## How to Set Variables in Your Deployment Platform

### Railway
1. Go to your Railway project
2. Navigate to Variables
3. Add each variable:
   - `MONGODB_URI`
   - `MONGODB_DATABASE`
   - `JWT_SECRET`
   - etc.

### Render
1. Go to your Render service
2. Navigate to Environment
3. Add new environment variables for each setting

### Streamlit Cloud
1. Go to your app settings
2. Navigate to Secrets
3. Add to `secrets.toml`:
```toml
MONGODB_URI = "mongodb+srv://..."
JWT_SECRET = "..."
```

### Heroku
1. Go to your app's Settings
2. Click "Reveal Config Vars"
3. Add each key-value pair

### Azure Container Instances / App Service
1. Go to your app's Configuration
2. Add Application Settings for each variable

## Verification

After setting the environment variables, the app should:
1. ✅ Start successfully (no crash on missing MongoDB URI)
2. ✅ Attempt to connect to the specified MongoDB database
3. ✅ Fall back gracefully if MongoDB is unavailable (for demo purposes)
4. ✅ Use the provided JWT_SECRET for token signing

## Troubleshooting

### "Connection refused" error
**Problem**: App logs show `localhost:27017: Connection refused`
**Solution**: Ensure `MONGODB_URI` environment variable is set in your deployment platform. The app is using the default value instead of your cloud database URI.

### Taxonomy file not found
**Problem**: App logs show `Taxonomy file not found: /mount/src/.../data/taxonomy.json`
**Solution**: This is expected in cloud deployments. The app will use a minimal fallback taxonomy. The AI features will work in basic mode without the full taxonomy.

### JWT errors
**Problem**: Token validation fails
**Solution**: Ensure all instances (Streamlit, FastAPI backend) are using the same `JWT_SECRET`. If you change the secret, existing tokens become invalid.

## Local Development

For local development, create a `.env` file in the project root:

```bash
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=sif_sentinel
JWT_SECRET=dev-jwt-secret
```

Never commit the `.env` file to version control!
