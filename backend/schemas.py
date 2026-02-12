from pydantic import BaseModel, HttpUrl, Field
from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime

class EventCreate(BaseModel):
    event_type: str = Field(..., example="order.completed")
    payload: Dict[str, Any]

class EventRead(EventCreate):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class SubscriptionCreate(BaseModel):
    event_type: str
    target_url: str # Use string for flexibility with localhost etc in dev
    secret_key: str

class SubscriptionRead(SubscriptionCreate):
    id: UUID
    is_active: bool

    class Config:
        from_attributes = True

class DeliveryAttemptRead(BaseModel):
    id: UUID
    event_id: UUID
    subscription_id: UUID
    status: str
    response_code: Optional[int]
    response_body: Optional[str]
    attempt_number: int
    scheduled_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
