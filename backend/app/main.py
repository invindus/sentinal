from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ROUTES
from app.api import blogs, scrape

app = FastAPI()

# ====== INCLUDE ROUTERS TO ENDPOINTS HERE ========
app.include_router(scrape.router)
app.include_router(blogs.router)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin for origin in origins if origin],
    allow_credentials = True,
    allow_methods = ['*'],
    allow_headers = ['*'],
)

@app.get("/health")
def health():
    return {"status": "ok"}

