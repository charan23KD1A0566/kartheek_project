"""
SIF Sentinel - Streamlit App
Main entry point: serves React frontend + runs FastAPI backend

DEPLOYMENT NOTE:
- Local: Frontend accesses backend at http://localhost:8000
- Streamlit Cloud: Backend subprocess can't be accessed from browser directly
  Solution: Deploy backend to a separate service (Railway, Render, etc.) and
  update FRONTEND_API_URL environment variable.
"""

import streamlit as st
import time
import logging
from pathlib import Path
import socket
import sys
import subprocess
import os
import requests
from urllib.parse import urljoin
from streamlit.web.server import WebsocketHeaders

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Backend URL - use external backend if provided, otherwise run locally
BACKEND_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")
USING_EXTERNAL_BACKEND = BACKEND_URL != "http://localhost:8000"

logger.info(f"Backend Mode: {'External' if USING_EXTERNAL_BACKEND else 'Local (subprocess)'}")
logger.info(f"Backend URL: {BACKEND_URL}")

# ============================================================================
# STREAMLIT CONFIGURATION  
# ============================================================================

st.set_page_config(
    page_title="SIF Sentinel",
    page_icon="⚠️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .main {padding: 0;}
    .block-container {padding: 0;}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# BACKEND (runs once)
# ============================================================================

@st.cache_resource
def start_backend():
    """Start FastAPI in a separate process (only if not using external backend)"""
    if USING_EXTERNAL_BACKEND:
        logger.info(f"✅ Using external backend: {BACKEND_URL}")
        return None
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if sock.connect_ex(('localhost', 8000)) == 0:
        sock.close()
        logger.info("Port 8000 already in use, skipping backend startup")
        return None
    sock.close()

    app_root = Path(__file__).resolve().parent
    backend_path = app_root / "backend"
    environment = os.environ.copy()
    for key in ("MONGODB_URI", "MONGODB_DATABASE", "JWT_SECRET", "DEBUG", "CORS_ORIGINS"):
        if key in st.secrets and not environment.get(key):
            environment[key] = str(st.secrets[key])
    environment["PYTHONPATH"] = str(backend_path) + os.pathsep + environment.get("PYTHONPATH", "")
    # Use localhost to allow both local and Streamlit Cloud access
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "localhost", "--port", "8000", "--log-level", "error"],
        cwd=str(backend_path),
        env=environment,
    )
    time.sleep(3)  # Give backend more time to start
    if process.poll() is not None:
        logger.error("FastAPI process exited during startup")
        return None
    
    # Verify backend is responding
    try:
        resp = requests.get("http://localhost:8000/api/health", timeout=5)
        if resp.status_code == 200:
            logger.info("✅ Local backend verified and ready")
        else:
            logger.warning(f"Backend health check returned {resp.status_code}")
    except Exception as e:
        logger.warning(f"Backend health check failed: {e}")
    
    return process

start_backend()

# ============================================================================
# FRONTEND
# ============================================================================

app_root = Path(__file__).resolve().parent
frontend_file = app_root / "frontend" / "dist" / "index.html"

if not frontend_file.exists():
    st.error(f"❌ Frontend not found: {frontend_file}")
    st.stop()

with open(str(frontend_file), 'r', encoding='utf-8') as f:
    html = f.read()

# Inline Vite assets because Streamlit does not serve frontend/dist as a static root.
assets_dir = frontend_file.parent / "assets"
js_file = next(assets_dir.glob("*.js"), None)
css_file = next(assets_dir.glob("*.css"), None)
if js_file is None or css_file is None:
    st.error(f"Frontend assets not found in {assets_dir}")
    st.stop()

with open(str(js_file), 'r', encoding='utf-8') as f:
    javascript = f.read()
with open(str(css_file), 'r', encoding='utf-8') as f:
    stylesheet = f.read()

# The production build may contain the deployment placeholder from Vite.
javascript = javascript.replace(
    "https://YOUR_BACKEND_URL/api",
    "/api"
)

html = html.replace(
    f'<script type="module" crossorigin src="/assets/{js_file.name}"></script>',
    f'<script type="module">{javascript}</script>'
)
html = html.replace(
    f'<link rel="stylesheet" crossorigin href="/assets/{css_file.name}">',
    f'<style>{stylesheet}</style>'
)

# Inject API config
html = html.replace("</head>", f"""
<script>
    // Configure API endpoint based on deployment mode
    const isDev = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    const apiBase = '{BACKEND_URL}/api';
    window.API_CONFIG = {{ baseURL: apiBase }};
    console.log('[SIF Sentinel] Environment:', isDev ? 'Development' : 'Production');
    console.log('[SIF Sentinel] API Base URL:', apiBase);
</script>
</head>""")

st.components.v1.html(html, height=1200, scrolling=True)
