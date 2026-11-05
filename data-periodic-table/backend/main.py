"""
FastAPI backend: verifies Firebase login tokens + reads a Google Sheet.
Run:  uvicorn main:app --reload --port 8000
"""
import os
import time
from pathlib import Path

import gspread
import firebase_admin
from firebase_admin import credentials, auth, firestore
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

# ---------------------------------------------------------------------------
# CONFIG: edit these two values
# ---------------------------------------------------------------------------
# The long ID in your sheet URL:
#   https://docs.google.com/spreadsheets/d/<<< THIS PART >>>/edit
SHEET_ID = os.getenv("SHEET_ID", "1kBEQG4bh92aEFbxOLEA3dmAFLM66sKqihRYqwyyIXxM")
# The name of the tab at the bottom of the sheet (case-sensitive)
WORKSHEET_NAME = os.getenv("WORKSHEET_NAME", "Data Template")
# ---------------------------------------------------------------------------

# --- Firebase Admin setup (uses the key file you download from the console) ---
BASE_DIR = Path(__file__).resolve().parent
SERVICE_ACCOUNT_FILE = Path(
    os.getenv("SERVICE_ACCOUNT_FILE", BASE_DIR / "ServiceAccountKey.json")
)

cred = credentials.Certificate(str(SERVICE_ACCOUNT_FILE))
firebase_admin.initialize_app(cred)
db = firestore.client()

# --- Google Sheets client: same key file, read-only permission ---
gc = gspread.service_account(
    filename=str(SERVICE_ACCOUNT_FILE),
    scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
)

app = FastAPI()

configured_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
]
allowed_origins = sorted(
    {
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        *configured_origins,
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_current_user(authorization: str = Header(default="")):
    """Reads 'Authorization: Bearer <token>' and verifies it with Firebase."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization.split(" ", 1)[1]
    try:
        return auth.verify_id_token(token)
    except Exception as e:
        if "Token used too early" in str(e):
            time.sleep(TOKEN_CLOCK_DRIFT_RETRY_SECONDS)
            try:
                return auth.verify_id_token(token)
            except Exception as retry_error:
                raise HTTPException(status_code=401, detail=f"Invalid token: {retry_error}")
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")


@app.post("/api/login")
def login(decoded=Depends(get_current_user)):
    """Called right after Google sign-in. Saves/updates the user in Firestore."""
    uid = decoded["uid"]
    profile = {
        "uid": uid,
        "name": decoded.get("name"),
        "email": decoded.get("email"),
        "picture": decoded.get("picture"),
        "last_login": firestore.SERVER_TIMESTAMP,
    }
    db.collection("users").document(uid).set(profile, merge=True)
    return {"ok": True, "user": {k: v for k, v in profile.items() if k != "last_login"}}


@app.get("/api/me")
def me(decoded=Depends(get_current_user)):
    """Example protected route: returns the saved user document."""
    doc = db.collection("users").document(decoded["uid"]).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="User not found")
    data = doc.to_dict()
    data.pop("last_login", None)
    return data


# ---------------------------------------------------------------------------
# Google Sheet data (protected: only logged-in users can call it)
# ---------------------------------------------------------------------------
_cache = {"time": 0, "data": None}
CACHE_SECONDS = 30  # avoids hitting Google's read quota on every refresh
TOKEN_CLOCK_DRIFT_RETRY_SECONDS = 3


@app.get("/api/sheet")
def read_sheet(decoded=Depends(get_current_user)):
    now = time.time()
    if _cache["data"] and now - _cache["time"] < CACHE_SECONDS:
        return _cache["data"]

    try:
        ws = gc.open_by_key(SHEET_ID).worksheet(WORKSHEET_NAME)
        values = ws.get_all_values()  # list of rows, each row is a list of strings
    except gspread.exceptions.SpreadsheetNotFound:
        raise HTTPException(
            status_code=404,
            detail="Sheet not found. Check SHEET_ID and share the sheet with the service account email.",
        )
    except gspread.exceptions.WorksheetNotFound:
        raise HTTPException(status_code=404, detail=f"Tab '{WORKSHEET_NAME}' not found.")
    except gspread.exceptions.APIError as e:
        raise HTTPException(status_code=502, detail=f"Google Sheets API error: {e}")

    if not values:
        data = {"headers": [], "rows": []}
    else:
        data = {"headers": values[0], "rows": values[1:]}

    _cache.update(time=now, data=data)
    return data