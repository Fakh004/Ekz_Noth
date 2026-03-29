from fastapi import FastAPI, Depends, HTTPException, Response, Cookie, Request
from sqlalchemy.orm import Session
import models, schemas, service
from database import engine, get_db
import uvicorn
import time
from fastapi.staticfiles import StaticFiles

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Personal Notes API")

@app.middleware("http")
async def log_process_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    print(f"[{request.method}] {request.url.path} completed in {process_time:.4f} secs")
    return response



def get_current_user(db: Session = Depends(get_db), session_id: str = Cookie(None)):
    user = service.get_user_by_session(db, session_id)
    if not user:
        raise HTTPException(status_code=401, detail="Вы не авторизованы")
    return user


@app.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return service.create_user(db, user)

@app.post("/login")
def login(response: Response, username: str, password: str, db: Session = Depends(get_db)):
    user = service.authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status_code=400, detail="Неверное имя пользователя или пароль")
    
    session_id = service.create_session(db, user.id)
    

    response.set_cookie(key="session_id", value=session_id, httponly=True)
    return {"msg": "Вход выполнен успешно"}

@app.post("/logout")
def logout(response: Response, session_id: str = Cookie(None), db: Session = Depends(get_db)):
    if session_id:
        db.query(models.Session).filter(models.Session.id == session_id).delete()
        db.commit()
    response.delete_cookie("session_id")
    return {"msg": "Вы вышли из системы"}


@app.get("/notes", response_model=list[schemas.NoteOut])
def list_notes(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return service.get_user_notes(db, user)

@app.post("/notes", response_model=schemas.NoteOut)
def add_note(note: schemas.NoteCreate, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return service.create_note(db, note, user.id)

@app.delete("/notes/{note_id}")
def remove_note(note_id: int, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    success = service.delete_note(db, note_id, user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Заметка не найдена или доступ запрещен")
    return {"msg": "Заметка удалена"}


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)