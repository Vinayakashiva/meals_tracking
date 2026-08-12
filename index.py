# Vercel looks for a WSGI-callable named `app` inside api/*.py.
# This just re-exports the real Flask app defined at the project root,
# so app.py stays the single source of truth for routes.
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app  # noqa: E402,F401
