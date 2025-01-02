from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from sqlalchemy.orm import Session
import secrets
from typing import Annotated
from pydantic import BaseModel
import uvicorn

from init_db import SessionLocal, init_db
from models import MovieDB

init_db()

app = FastAPI()
security = HTTPBasic()

users_db = {
    "admin": "admin",
    "user": "password"
}

def verify_credentials(credentials: HTTPBasicCredentials | None = Depends(security)):
    print(credentials)
    correct_password = secrets.compare_digest(credentials.password, users_db.get(credentials.username, ""))

    if not correct_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
            headers={"Authenticate": "Basic"},
        )
    return credentials.username

class Movie(BaseModel):
    id: int
    title: str
    director: str
    release_year: int
    rating: float

    class Config:
        orm_mode = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return RedirectResponse(url="/docs")

@app.get("/movies", response_model=list[Movie])
def get_movies(username: Annotated[str, Depends(verify_credentials)], db: Session = Depends(get_db)):
    return db.query(MovieDB).all()

@app.post("/movies", response_model=Movie)
def create_movie(movie: Movie,username: Annotated[str, Depends(verify_credentials)], db: Session = Depends(get_db)):
    db_movie = MovieDB(**movie.dict())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie

@app.get("/movies/{id}", response_model=Movie)
def get_movie(id: int,username: Annotated[str, Depends(verify_credentials)], db: Session = Depends(get_db)):
    movie = db.query(MovieDB).filter(MovieDB.id == id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

@app.delete("/movies/{id}", response_model=Movie)
def delete_movie(id: int, username: Annotated[str, Depends(verify_credentials)], db: Session = Depends(get_db)):
    movie = db.query(MovieDB).filter(MovieDB.id == id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    db.delete(movie)
    db.commit()
    return movie

if __name__ == "__main__":
    uvicorn.run(f"{__name__}:app", reload=True)