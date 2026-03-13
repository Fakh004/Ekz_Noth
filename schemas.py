from pydantic import BaseModel, Field

class NotificationCreate(BaseModel):
    message: str = Field(..., min_length=1, max_length=500, description="Текст уведомления не может быть пустым")