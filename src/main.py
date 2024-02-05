from fastapi import FastAPI

app = FastAPI(title="Auction apps")

@app.get("/")
def index():
    return "Hello world"