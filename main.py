from fastapi import FastAPI, HTTPException, Header
from models import init_models
import service
from schemas import NotificationCreate

app = FastAPI()

@app.post("/")
def hello():
    return  "Hello World"

@app.post("/register")
async def reg(username: str, password: str):
    return service.register_user(username, password)

@app.post("/login")
async def log(username: str, password: str):
    return service.login_user(username, password)

@app.post("/logout")
async def logout(user_id: str = Header(None)):
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID is missing")
    result = service.logout_user(user_id)
    if result["status"] == 404:
        raise HTTPException(status_code=404, detail=result["msg"])
    return result

@app.post("/create_notification")
async def create_notification(notification: NotificationCreate, user_id: str = Header(None)):
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID is missing")
    return service.create_notif(user_id, notification.message)

@app.get("/notifications")
async def get_notifications():
    return service.get_all_notifs()

@app.delete("/notifications/delete/{notif_id}")
async def delete_by_id_only(notif_id: int):
    result = service.delete_notification_by_id(notif_id)    
    if result["status"] == 404:
        raise HTTPException(status_code=404, detail=result["msg"])
    return result


if __name__ == "__main__":
    init_models()
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)