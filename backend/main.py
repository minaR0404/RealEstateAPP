from fastapi import FastAPI, HTTPException
from typing import List
from database import SessionLocal, engine
import models, schemas, crud

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Real Estate API")

@app.get("/properties/", response_model=List[schemas.Property])
def read_properties(skip: int = 0, limit: int = 10):
    db = SessionLocal()
    try:
        return crud.get_properties(db, skip=skip, limit=limit)
    finally:
        db.close()

@app.get("/properties/{property_id}", response_model=schemas.Property)
def read_property(property_id: int):
    db = SessionLocal()
    try:
        property_data = crud.get_property(db, property_id)
        if property_data is None:
            raise HTTPException(status_code=404, detail="Property not found")
        return property_data
    finally:
        db.close()
