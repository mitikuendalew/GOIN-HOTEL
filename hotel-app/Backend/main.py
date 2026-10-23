from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
import os

# 1. SETUP THE DATABASE (SQLite)
DATABASE_URL = "sqlite:///./Goin_hotel.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class BookingModel(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    guest_name = Column(String, index=True)
    room_type = Column(String)
    check_in = Column(String)
    check_out = Column(String)
    phone_number = Column(String)

Base.metadata.create_all(bind=engine)

# 2. SETUP THE SERVER
app = FastAPI(
    title="Gion Hotel Booking API",
    description="API for managing hotel bookings",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- NEW: SERVE THE FRONTEND HTML DIRECTLY FROM THE BACKEND ---
@app.get("/", response_class=HTMLResponse)
def serve_homepage():
    # Looks for goin.html in the parent folder or frontend folder
    html_path = os.path.join("..", "frontend", "goin.html")
    if not os.path.exists(html_path):
        html_path = "goin.html"
    
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

# Pydantic schema
class BookingCreate(BaseModel):
    guest_name: str
    room_type: str
    check_in: str
    check_out: str
    phone_number: str

# API ENDPOINTS
@app.get("/bookings")
def get_bookings(db: Session = Depends(get_db)):
    return db.query(BookingModel).all()

@app.post("/bookings")
def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    new_booking = BookingModel(
        guest_name=booking.guest_name,
        room_type=booking.room_type,
        check_in=booking.check_in,
        check_out=booking.check_out,
        phone_number=booking.phone_number
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return {"message": "Booking successful!", "booking": new_booking}

@app.delete("/bookings/{booking_id}")
def delete_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(BookingModel).filter(BookingModel.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    db.delete(booking)
    db.commit()
    return {"message": f"Booking ID {booking_id} has been successfully canceled."}