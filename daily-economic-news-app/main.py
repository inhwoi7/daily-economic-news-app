from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Annotated, List, Optional
from datetime import timedelta, datetime
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import pytz
import os
from pathlib import Path

from database import SessionLocal, engine, Base
import models, auth
import email_builder
import send_email

BASE_DIR = Path(__file__).parent

# Configure logging for APScheduler
logging.basicConfig(level=logging.INFO)
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

# Pydantic models for authentication
class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr # Added email field to UserCreate

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Pydantic models for Preferences
class PreferenceBase(BaseModel):
    email_time: str = "08:10" # HH:MM format

class PreferenceCreate(PreferenceBase):
    pass

class Preference(PreferenceBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

class NewsSourceBase(BaseModel):
    name: str
    url: str
    is_active: bool = True

class NewsSourceCreate(NewsSourceBase):
    pass

class NewsSource(NewsSourceBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

class StockBase(BaseModel):
    symbol: str
    is_active: bool = True

class StockCreate(StockBase):
    pass

class Stock(StockBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

class CurrencyBase(BaseModel):
    symbol: str
    is_active: bool = True

class CurrencyCreate(CurrencyBase):
    pass

class Currency(CurrencyBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

# Pydantic model for User response
class User(BaseModel):
    id: int
    username: str
    email: EmailStr # Added email field to User response model
    preferences: List[Preference] = []
    news_sources: List[NewsSource] = []
    stocks: List[Stock] = []
    currencies: List[Currency] = []

    class Config:
        from_attributes = True


app = FastAPI()
scheduler = BackgroundScheduler()

# Mount the static directory to serve frontend files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = auth.decode_access_token(token)
    if payload is None:
        raise credentials_exception
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

def scheduled_email_task():
    """
    Background task to send daily emails to all users based on their preferences.
    """
    with SessionLocal() as db:
        now = datetime.now(pytz.utc).astimezone(pytz.timezone('Asia/Seoul')) # Assuming Seoul timezone for scheduling
        current_time_str = now.strftime("%H:%M")
        
        users = db.query(models.User).all()
        print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Running scheduled email task for {len(users)} users.")

        for user in users:
            preference = db.query(models.Preference).filter(models.Preference.owner_id == user.id).first()
            email_time = preference.email_time if preference else "08:10" # Default if no preference set

            if user.email and email_time == current_time_str:
                print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Sending email to {user.username} at {email_time}...")
                try:
                    email_html_content = email_builder.build_daily_email_content(user.id, user.email, db)
                    
                    gmail_service = send_email.get_gmail_service()
                    if not gmail_service:
                        print(f"Error: Failed to initialize Gmail service for user {user.username}. Skipping email.")
                        continue

                    message = send_email.create_message(
                        sender="me", 
                        to=user.email, 
                        subject=f"Daily Economic News Summary for {user.username} ({email_time})", 
                        message_text=email_html_content
                    )
                    send_email.send_message(gmail_service, "me", message)
                    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Email sent successfully to {user.email}")
                except Exception as e:
                    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Error sending email to {user.email}: {e}")
            else:
                print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Skipping email for {user.username}. Email: {user.email}, Preferred time: {email_time}, Current time: {current_time_str}")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    scheduler.add_job(scheduled_email_task, 'interval', minutes=1, id='daily_email_check') # Run every minute for checking
    scheduler.start()
    print("Scheduler started.")

@app.on_event("shutdown")
def on_shutdown():
    scheduler.shutdown()
    print("Scheduler shutdown.")

@app.post("/register", response_model=UserCreate)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password, email=user.email) # Save email
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return user

@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- User Preferences Endpoints ---

@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: Annotated[models.User, Depends(get_current_user)]):
    return current_user

# Preferences (Email Time)
@app.post("/preferences/", response_model=Preference)
def create_preference(preference: PreferenceCreate, current_user: Annotated[models.User, Depends(get_current_user)], db: Session = Depends(get_db)):
    db_preference = db.query(models.Preference).filter(models.Preference.owner_id == current_user.id).first()
    if db_preference: # Update existing preference if it exists
        db_preference.email_time = preference.email_time
    else:
        db_preference = models.Preference(**preference.dict(), owner_id=current_user.id)
        db.add(db_preference)
    db.commit()
    db.refresh(db_preference)
    return db_preference

@app.get("/preferences/", response_model=List[Preference])
def read_preferences(current_user: Annotated[models.User, Depends(get_current_user)], db: Session = Depends(get_db)):
    return db.query(models.Preference).filter(models.Preference.owner_id == current_user.id).all()

# News Sources
@app.post("/news_sources/", response_model=NewsSource)
def create_news_source(news_source: NewsSourceCreate, current_user: Annotated[models.User, Depends(get_current_user)], db: Session = Depends(get_db)):
    db_news_source = models.NewsSource(**news_source.dict(), owner_id=current_user.id)
    db.add(db_news_source)
    db.commit()
    db.refresh(db_news_source)
    return db_news_source

@app.get("/news_sources/", response_model=List[NewsSource])
def read_news_sources(current_user: Annotated[models.User, Depends(get_current_user)], db: Session = Depends(get_db)):
    return db.query(models.NewsSource).filter(models.NewsSource.owner_id == current_user.id).all()

@app.put("/news_sources/{news_source_id}", response_model=NewsSource)
def update_news_source(news_source_id: int, news_source: NewsSourceCreate, current_user: Annotated[models.User, Depends(get_current_user)], db: Session = Depends(get_db)):
    db_news_source = db.query(models.NewsSource).filter(models.NewsSource.id == news_source_id, models.NewsSource.owner_id == current_user.id).first()
    if not db_news_source:
        raise HTTPException(status_code=404, detail="News source not found")
    for key, value in news_source.dict().items():
        setattr(db_news_source, key, value)
    db.commit()
    db.refresh(db_news_source)
    return db_news_source

@app.delete("/news_sources/{news_source_id}")
def delete_news_source(news_source_id: int, current_user: Annotated[models.User, Depends(get_current_user)], db: Session = Depends(get_db)):
    db_news_source = db.query(models.NewsSource).filter(models.NewsSource.id == news_source_id, models.NewsSource.owner_id == current_user.id).first()
    if not db_news_source:
        raise HTTPException(status_code=404, detail="News source not found")
    db.delete(db_news_source)
    db.commit()
    return {"message": "News source deleted successfully"}

# Stocks
@app.post("/stocks/", response_model=Stock)
def create_stock(stock: StockCreate, current_user: Annotated[models.User, Depends(get_current_user)], db: Session = Depends(get_db)):
    db_stock = models.Stock(**stock.dict(), owner_id=current_user.id)
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock

@app.get("/stocks/", response_model=List[Stock])
def read_stocks(current_user: Annotated[models.User, Depends(get_current_user)], db: Session = Depends(get_db)):
    return db.query(models.Stock).filter(models.Stock.owner_id == current_user.id).all()

@app.put("/stocks/{stock_id}", response_model=Stock)
def update_stock(stock_id: int, stock: StockCreate, current_user: Annotated[models.User, Depends(get_current_user)], db: Session = Depends(get_db)):
    db_stock = db.query(models.Stock).filter(models.Stock.id == stock_id, models.Stock.owner_id == current_user.id).first()
    if not db_stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    for key, value in stock.dict().items():
        setattr(db_stock, key, value)
    db.commit()
    db.refresh(db_stock)
    return db_stock

@app.delete("/stocks/{stock_id}")
def delete_stock(stock_id: int, current_user: Annotated[models.User, Depends(get_current_user)], db: Session = Depends(get_db)):
    db_stock = db.query(models.Stock).filter(models.Stock.id == stock_id, models.Stock.owner_id == current_user.id).first()
    if not db_stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    db.delete(db_stock)
    db.commit()
    return {"message": "Stock deleted successfully"}

# Currencies
@app.post("/currencies/", response_model=Currency)
def create_currency(currency: CurrencyCreate, current_user: Annotated[models.User, Depends(get_current_user)], db: Session = Depends(get_db)):
    db_currency = models.Currency(**currency.dict(), owner_id=current_user.id)
    db.add(db_currency)
    db.commit()
    db.refresh(db_currency)
    return db_currency

@app.get("/currencies/", response_model=List[Currency])
def read_currencies(current_user: Annotated[models.User, Depends(get_current_user)], db: Session = Depends(get_db)):
    return db.query(models.Currency).filter(models.Currency.owner_id == current_user.id).all()

@app.put("/currencies/{currency_id}", response_model=Currency)
def update_currency(currency_id: int, currency: CurrencyCreate, current_user: Annotated[models.User, Depends(get_current_user)], db: Session = Depends(get_db)):
    db_currency = db.query(models.Currency).filter(models.Currency.id == currency_id, models.Currency.owner_id == current_user.id).first()
    if not db_currency:
        raise HTTPException(status_code=404, detail="Currency not found")
    for key, value in currency.dict().items():
        setattr(db_currency, key, value)
    db.commit()
    db.refresh(db_currency)
    return db_currency

@app.delete("/currencies/{currency_id}")
def delete_currency(currency_id: int, current_user: Annotated[models.User, Depends(get_current_user)], db: Session = Depends(get_db)):
    db_currency = db.query(models.Currency).filter(models.Currency.id == currency_id, models.Currency.owner_id == current_user.id).first()
    if not db_currency:
        raise HTTPException(status_code=404, detail="Currency not found")
    db.delete(db_currency)
    db.commit()
    return {"message": "Currency deleted successfully"}

from fastapi.responses import HTMLResponse

@app.get("/preview-email", response_class=HTMLResponse)
def preview_daily_email(current_user: Annotated[models.User, Depends(get_current_user)], db: Session = Depends(get_db)):
    email_html_content = email_builder.build_daily_email_content(current_user.id, current_user.email, db)
    return email_html_content

@app.post("/send-daily-email")
async def send_daily_email_endpoint(current_user: Annotated[models.User, Depends(get_current_user)], db: Session = Depends(get_db)):
    if not current_user.email:
        raise HTTPException(status_code=400, detail="User has no email configured.")
    
    # Fetch email time preference
    preference = db.query(models.Preference).filter(models.Preference.owner_id == current_user.id).first()
    email_time = preference.email_time if preference else "08:10" # Default if no preference set

    email_html_content = email_builder.build_daily_email_content(current_user.id, current_user.email, db)
    
    gmail_service = send_email.get_gmail_service()
    if not gmail_service:
        raise HTTPException(status_code=500, detail="Failed to initialize Gmail service. Check server logs.")

    message = send_email.create_message(
        sender="me", 
        to=current_user.email, 
        subject=f"Daily Economic News Summary for {current_user.username} ({email_time})", 
        message_text=email_html_content
    )
    send_email.send_message(gmail_service, "me", message)
    
    return {"message": "Daily email sent successfully (or attempted)."}


@app.get("/")
def read_root():
    return FileResponse(str(BASE_DIR / 'static' / 'index.html'))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


