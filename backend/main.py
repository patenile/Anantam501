
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import models
import schemas
import auth
import database
from sqlalchemy.exc import IntegrityError

app = FastAPI()

models.Base.metadata.create_all(bind=database.engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Backend is running!"}

@app.post("/auth/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    print("[REGISTER ENTRY] Entered register endpoint", flush=True)
    import sys
    debug_msg = f"[REGISTER DEBUG] user: {user}, email: {getattr(user, 'email', None)}, password: {getattr(user, 'password', None)}, password type: {type(getattr(user, 'password', None))}\n"
    print(debug_msg, flush=True)
    import traceback
    try:
        with open("/tmp/register_debug.log", "a") as f:
            f.write(debug_msg)
    except Exception as e:
        pass
    # Enforce minimum password length
    if len(user.password) < 8:
        raise HTTPException(status_code=422, detail="Password must be at least 8 characters long")
    try:
        hashed_password = auth.get_password_hash(user.password)
        db_user = models.User(email=user.email, hashed_password=hashed_password, full_name=user.full_name)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")
    except Exception as e:
        tb = traceback.format_exc()
        print(f"[REGISTER ERROR] {e}\n{tb}", flush=True)
        try:
            with open("/tmp/register_debug.log", "a") as f:
                f.write(f"[REGISTER ERROR] {e}\n{tb}\n")
        except Exception:
            pass
        raise HTTPException(status_code=500, detail="Internal Server Error: see backend logs for details")

@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = auth.create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = auth.decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    user = db.query(models.User).filter(models.User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.get("/users/me", response_model=schemas.UserOut)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user
