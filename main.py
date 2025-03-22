from fastapi import FastAPI
from api import article_retriever

app = FastAPI()

app.include_router(article_retriever.router, prefix="/articles", tags=["Articles"])

@app.get("/")
def root():
    return {"message": "Welcome to VBP FastAPI Backend"}
