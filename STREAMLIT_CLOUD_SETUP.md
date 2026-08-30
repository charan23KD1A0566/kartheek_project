# Streamlit Cloud Deployment Setup Guide

## Quick Start

Your app is deployed on **Streamlit Cloud** and needs environment secrets configured to work properly.

### Step 1: Access Your Streamlit Cloud Dashboard

1. Go to [https://share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Find your app in the list (should be named after your GitHub repo: `kartheek_project`)
4. Click the **⋮** (three dots) menu in the top-right corner
5. Select **Settings**

### Step 2: Add Secrets in Streamlit Cloud

Click on the **Secrets** section and add the following secrets:

#### **CRITICAL: MongoDB Connection String**

Add this secret with your actual MongoDB connection string:

```
MONGODB_URI=mongodb+srv://admin:PASSWORD@sif-sentinel.rmkwxs6.mongodb.net/sif_sentinel?retryWrites=true&w=majority
```

Replace `PASSWORD` with your actual MongoDB Atlas password.

⚠️ **This is the most critical setting.** Without it, your app will fail to connect to the database.

#### JWT Secret (Optional but Recommended)

```
JWT_SECRET=s2eqgXDC_iMLRiZSOQUVyLfQcxSOgvJ_tWh5iJbSfAA
```

Use the same JWT_SECRET from your local `.env` file for consistency.

#### Database Name (Optional)

```
MONGODB_DATABASE=sif_sentinel
```

#### Frontend URL (Optional)

```
FRONTEND_API_URL=https://your-streamlit-url.streamlit.app
```

### Step 3: Restart Your App

After adding secrets:

1. Click the **⋮** menu again
2. Select **Reboot app**
3. Wait for the app to restart (2-3 minutes)

The app should now connect to MongoDB and start properly!

## Streamlit Secrets Format

In Streamlit Cloud, secrets are stored in a `secrets.toml` file. The UI shows them as key-value pairs, but they're automatically converted to environment variables.

Your `app.py` already reads these secrets and passes them to the FastAPI backend:

```python
for key in ("MONGODB_URI", "MONGODB_DATABASE", "JWT_SECRET", "DEBUG", "CORS_ORIGINS"):
    if key in st.secrets and not environment.get(key):
        environment[key] = str(st.secrets[key])
```

## Verification

After setup, check the app logs:

1. Click your app name on the dashboard
2. Look for logs at the bottom showing:
   - `[OK] Connected to MongoDB: sif_sentinel` ✅
   - `[OK] SIF Sentinel is ready to serve requests` ✅
   - No `Connection refused` errors ✅

## Troubleshooting

### "Connection refused" Error

**Symptom:** App logs show `localhost:27017: Connection refused`

**Fix:** 
- Verify `MONGODB_URI` is set in Streamlit Secrets (check Settings → Secrets)
- Confirm the connection string includes your MongoDB Atlas password
- Reboot the app after adding/changing the secret

### "Taxonomy file not found" Warning

**Symptom:** App logs show `Taxonomy file not found: /mount/src/.../data/taxonomy.json`

**Expected behavior:** This is normal in cloud deployments. The app uses a fallback taxonomy and will still work. AI features may have reduced functionality without the full taxonomy.

### App Won't Start

**Check these in order:**
1. MONGODB_URI is set in Streamlit Secrets
2. MongoDB Atlas connection string includes correct password
3. Firewall allows connections from Streamlit Cloud (check MongoDB Atlas Network Access)
4. App was rebooted after adding secrets

## MongoDB Atlas Network Access Setup

If your app still can't connect to MongoDB:

1. Go to [MongoDB Atlas](https://cloud.mongodb.com)
2. Go to your cluster → Network Access
3. Click "Add IP Address"
4. Select "Allow Access from Anywhere" (or specific Streamlit IP if available)
5. Confirm

## Environment Variables Reference

| Variable | Required | Example | Notes |
|----------|----------|---------|-------|
| `MONGODB_URI` | ✅ Yes | `mongodb+srv://admin:pass@cluster.mongodb.net/...` | Must be cloud MongoDB Atlas URI, not localhost |
| `MONGODB_DATABASE` | ❌ Optional | `sif_sentinel` | Defaults to `sif_sentinel` |
| `JWT_SECRET` | ❌ Optional | Long random string | Defaults to demo key if not set |
| `CORS_ORIGINS` | ❌ Optional | `https://yourdomain.com` | Defaults to localhost URLs |
| `FRONTEND_API_URL` | ❌ Optional | `https://yourdomain.com/api` | Defaults to `http://localhost:5173` |
| `DEBUG` | ❌ Optional | `False` | Defaults to `True` (set to `False` for production) |

## How Streamlit Secrets Work

When you add secrets in Streamlit Cloud:

1. **Stored securely** on Streamlit's servers
2. **Injected as environment variables** when your app runs
3. **Accessed in code** via `st.secrets` or `os.getenv()`
4. **Never logged or exposed** in public app logs

Example in code:
```python
mongodb_uri = st.secrets.get("MONGODB_URI", os.getenv("MONGODB_URI"))
```

## Next Steps

1. ✅ Set `MONGODB_URI` in Streamlit Cloud Secrets
2. ✅ Reboot the app
3. ✅ Check logs to verify connection
4. ✅ Test the app features

Your app should now be fully functional! 🚀
