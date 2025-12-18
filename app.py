# app.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
import string
import random

app = FastAPI()

# In-memory storage
url_db = {}

class ShortenRequest(BaseModel):
    long_url: HttpUrl  # validates the URL format

def generate_short_id(length=6):
    characters = string.ascii_letters + string.digits
    # try until we get a non-colliding ID
    while True:
        sid = ''.join(random.choice(characters) for _ in range(length))
        if sid not in url_db:
            return sid

@app.post("/shorten")
async def shorten_url(req: ShortenRequest, request: Request):
    short_id = generate_short_id()
    url_db[short_id] = req.long_url
    # construct full short URL using the current host
    host = request.url.hostname or "127.0.0.1"
    port = request.url.port or 8000
    full_short = f"http://{host}:{port}/{short_id}"
    # Optional: print db to console so you can screenshot it
    print("Current URL DB:", url_db)
    return {"short_url_id": short_id, "short_url": full_short, "original_url": req.long_url}

@app.get("/{short_id}")
async def redirect(short_id: str):
    if short_id not in url_db:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return RedirectResponse(url_db[short_id])
