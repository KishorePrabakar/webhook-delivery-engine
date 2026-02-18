from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
import uuid
import json

from database import engine, Base, get_db
from models import Event, Subscription, DeliveryAttempt
from schemas import EventCreate, EventRead, SubscriptionCreate, SubscriptionRead
from arq import create_pool
from arq.connections import RedisSettings
import os

app = FastAPI(title="Webhook platform Engine")

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.on_event("startup")
async def startup():
    # Create tables (In production use Alembic)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    app.state.redis = await create_pool(RedisSettings.from_dsn(REDIS_URL))

@app.on_event("shutdown")
async def shutdown():
    await app.state.redis.close()

@app.post("/api/v1/events", response_model=EventRead)
async def create_event(event_data: EventCreate, db: AsyncSession = Depends(get_db)):
    db_event = Event(
        event_type=event_data.event_type,
        payload=event_data.payload
    )
    db.add(db_event)
    await db.commit()
    await db.refresh(db_event)
    
    # Trigger webhooks in background via arq
    await app.state.redis.enqueue_job('dispatch_event', str(db_event.id))
    
    return db_event

@app.get("/api/v1/subscriptions", response_model=List[SubscriptionRead])
async def list_subscriptions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Subscription))
    return result.scalars().all()

@app.post("/api/v1/subscriptions", response_model=SubscriptionRead)
async def create_subscription(sub_data: SubscriptionCreate, db: AsyncSession = Depends(get_db)):
    db_sub = Subscription(
        event_type=sub_data.event_type,
        target_url=sub_data.target_url,
        secret_key=sub_data.secret_key
    )
    db.add(db_sub)
    await db.commit()
    await db.refresh(db_sub)
    return db_sub

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Just keep the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/v1/internal/broadcast")
async def internal_broadcast(data: Dict[str, Any]):
    # This endpoint is used by the worker to push updates to the UI
    await manager.broadcast(json.dumps(data))
    return {"status": "ok"}
