import uuid
from sqlalchemy.orm import Session
import models, schemas, auth


def create_user(db: Session, user_data: schemas.UserCreate):
    hashed_pwd = auth.hash_password(user_data.password)
    db_user = models.User(
        username=user_data.username,
        email=user_data.email,
        password=hashed_pwd,
        is_admin=False 
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username_or_email: str, password: str):
    user = db.query(models.User).filter(
        (models.User.username == username_or_email) | (models.User.email == username_or_email)
    ).first()
    
    if not user or not auth.verify_password(password, user.password):
        return None
    return user


def create_session(db: Session, user_id: int):
    session_id = str(uuid.uuid4())
    new_session = models.Session(id=session_id, user_id=user_id)
    db.add(new_session)
    db.commit()
    return session_id

def get_user_by_session(db: Session, session_id: str):
    if not session_id:
        return None
    session_record = db.query(models.Session).filter(models.Session.id == session_id).first()
    if session_record:
        return session_record.user
    return None


def create_note(db: Session, note_data: schemas.NoteCreate, user_id: int):
    new_note = models.Note(**note_data.model_dump(), user_id=user_id)
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note

def get_user_notes(db: Session, user: models.User):
    if user.is_admin:
        return db.query(models.Note).all()
    return user.notes

def delete_note(db: Session, note_id: int, user_id: int):
    note = db.query(models.Note).filter(models.Note.id == note_id, models.Note.user_id == user_id).first()
    if note:
        db.delete(note)
        db.commit()
        return True
    return False