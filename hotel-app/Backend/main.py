from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import date

# 1. SETUP THE DATABASE (SQLite)
DATABASE_URL = "sqlite:///./Goin_hotel.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define what a "Booking" looks like in the database
class BookingModel(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    guest_name = Column(String, index=True)
    room_type = Column(String)
    check_in = Column(String)
    check_out = Column(String)
    phone_number = Column(String)  # <--- Added this new database column

# Create the database tables
Base.metadata.create_all(bind=engine)

# 2. SETUP THE SERVER (FastAPI)
app = FastAPI(
    title="Gion Hotel Booking API",
    description="API for managing hotel bookinkgs",
    version="1.0.0"
)

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper function to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 3. API ENDPOINTS (Routes)

# Route to get all bookings
@app.get("/bookings")
def get_bookings(db: Session = Depends(get_db)):
    return db.query(BookingModel).all()

# Route to create a new booking
@app.post("/bookings")
def create_booking(guest_name: str, room_type: str, check_in: str, check_out: str, phone_number: str, db: Session = Depends(get_db)):
    new_booking = BookingModel(
        guest_name=guest_name,
        room_type=room_type,
        check_in=check_in,
        check_out=check_out,
        phone_number=phone_number  # <--- Saved to database
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return {"message": "Booking successful!", "booking": new_booking}

# Route to delete a booking by its ID number
@app.delete("/bookings/{booking_id}")
def delete_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(BookingModel).filter(BookingModel.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    db.delete(booking)
    db.commit()
    return {"message": f"Booking ID {booking_id} has been successfully canceled."}