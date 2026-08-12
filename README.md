# Hackathon Meals Register — Flask version

Converted from Vercel serverless functions to a single Flask app.

## Files
- `app.py` — Flask app: serves `index.html` and exposes `/api/team` (GET) and `/api/mark` (POST)
- `_sheets.py` — Google Sheets connector (unchanged, framework-agnostic)
- `index.html` — frontend (unchanged)
- `requirements.txt` — dependencies

## Local setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env with your service account email, private key, and sheet ID

python app.py
```

Open http://localhost:5000

## Notes on the conversion
- The old `mark.py` / `team.py` each subclassed `BaseHTTPRequestHandler` (Vercel's
  Python function format). Both are now just route functions in `app.py` using
  Flask's `request` / `jsonify`, so the manual JSON parsing/response boilerplate
  is gone.
- `_sheets.py` needed no changes — it never touched the HTTP layer.
- `index.html` needed no changes — it calls `/api/team` and `/api/mark` by
  relative path, which Flask now serves directly instead of Vercel's `/api/*`
  routing convention.

## Deploying to Vercel

Vercel's Python runtime doesn't run `app.run()` — it needs a WSGI-callable
`app` object exposed under `api/`, with a `vercel.json` routing everything
to it. That's what `api/index.py` and `vercel.json` in this folder do
(they just re-export the same Flask `app` from `app.py` at the root, so
there's only one copy of the routes to maintain).

Project layout for Vercel:
```
.
├── app.py          # Flask app + routes (source of truth)
├── _sheets.py
├── index.html
├── api/
│   └── index.py    # re-exports app.py's `app` for Vercel's Python runtime
├── vercel.json      # rewrites all paths to api/index.py
└── requirements.txt
```

Steps:
```bash
npm i -g vercel     # if you don't have the CLI
vercel
```
Then in the Vercel dashboard (or `vercel env add`), set:
`GOOGLE_SERVICE_ACCOUNT_EMAIL`, `GOOGLE_PRIVATE_KEY`, `GOOGLE_SHEET_ID`.

## Deploying elsewhere (Render, Railway, Fly.io, a VM, etc.)
Any plain WSGI host works — run with gunicorn instead of the Flask dev server:

```bash
gunicorn app:app --bind 0.0.0.0:$PORT
```

Set the same three environment variables in that host's config.

## Concurrent users (e.g. 3–4 people marking meals at once)
This should cause no real problems at that scale:
- There's no shared in-memory state — every request reads/writes Google
  Sheets directly, and Vercel spins up function instances independently
  per request, so concurrent requests don't interfere with each other.
- The Google Sheets API allows 60 read/write requests per minute per
  service account — far more than 3-4 people tapping buttons will produce.
- The only theoretical race: two people marking the *same* member's *same*
  meal in the same instant would result in last-write-wins (no crash, no
  error, just one update "winning"). Very unlikely at a check-in desk with
  people tracking different members.
