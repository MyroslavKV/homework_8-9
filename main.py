from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uvicorn

from init_db import SessionLocal, init_db
from models import MovieDB

init_db()

app = FastAPI()

class Movie(BaseModel):
    id
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
def get_movies(db: Session = Depends(get_db)):
    return db.query(MovieDB).all()

@app.post("/movies", response_model=Movie)
def create_movie(movie: Movie, db: Session = Depends(get_db)):
    db_movie = MovieDB(**movie.dict())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie

@app.get("/movies/{id}", response_model=Movie)
def get_movie(id: int, db: Session = Depends(get_db)):
    movie = db.query(MovieDB).filter(MovieDB.id == id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

@app.delete("/movies/{id}", response_model=Movie)
def delete_movie(id: int, db: Session = Depends(get_db)):
    movie = db.query(MovieDB).filter(MovieDB.id == id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    db.delete(movie)
    db.commit()
    return movie

if __name__ == "__main__":
    uvicorn.run(f"{__name__}:app", reload=True)