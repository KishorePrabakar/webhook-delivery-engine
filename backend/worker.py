import asyncio
import httpx
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from models import Event, Subscription, DeliveryAttempt
from database import DATABASE_URL
from utils import sign_payload
from arq.connections import RedisSettings
from datetime import datetime, timedelta
import uuid
import json

async def broadcast_update(attempt):
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                "http://backend:8000/api/v1/internal/broadcast",
                json={
                    "type": "delivery_update",
                    "id": str(attempt.id),
                    "event_id": str(attempt.event_id),
                    "status": attempt.status,
                    "response_code": attempt.response_code,
                    "attempt_number": attempt.attempt_number,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        except Exception:
            pass

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def dispatch_event(ctx, event_id: str):
    async with AsyncSessionLocal() as db:
        # 1. Fetch event
        result = await db.execute(select(Event).where(Event.id == uuid.UUID(event_id)))
        event = result.scalar_one_or_none()
        if not event:
            return

        # 2. Find subscriptions
        result = await db.execute(
            select(Subscription).where(
                Subscription.event_type == event.event_type,
                Subscription.is_active == True
            )
        )
        subs = result.scalars().all()

        for sub in subs:
            # Create delivery attempt
            attempt = DeliveryAttempt(
                event_id=event.id,
                subscription_id=sub.id,
                status="pending",
                attempt_number=1
            )
            db.add(attempt)
            await db.commit()
            await db.refresh(attempt)
            
            # Enqueue the actual delivery
            await ctx['redis'].enqueue_job('deliver_webhook', str(attempt.id))

async def deliver_webhook(ctx, attempt_id: str):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(DeliveryAttempt).where(DeliveryAttempt.id == uuid.UUID(attempt_id)))
        attempt = result.scalar_one_or_none()
        if not attempt:
            return

        result = await db.execute(select(Subscription).where(Subscription.id == attempt.subscription_id))
        sub = result.scalar_one_or_none()
        result = await db.execute(select(Event).where(Event.id == attempt.event_id))
        event = result.scalar_one_or_none()

        if not sub or not event:
            return

        # Sign payload
        signature = sign_payload(event.payload, sub.secret_key)
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    sub.target_url,
                    json=event.payload,
                    headers={
                        "Content-Type": "application/json",
                        "X-Webhook-Signature": signature,
                        "X-Webhook-Event-Type": event.event_type,
                        "X-Webhook-Delivery-Id": str(attempt.id)
                    }
                )
                
                attempt.response_code = response.status_code
                attempt.response_body = response.text[:1000] # Cap size
                
                if 200 <= response.status_code < 300:
                    attempt.status = "success"
                else:
                    await handle_retry(ctx, db, attempt)
                
                # Broadcast update
                await broadcast_update(attempt)
                    
        except Exception as e:
            attempt.response_body = str(e)
            await handle_retry(ctx, db, attempt)
            await broadcast_update(attempt)
            
        attempt.created_at = datetime.utcnow()
        await db.commit()

async def handle_retry(ctx, db, attempt):
    max_retries = 5
    if attempt.attempt_number >= max_retries:
        attempt.status = "dlq"
    else:
        attempt.status = "retrying"
        # Exponential backoff: 10s, 20s, 40s, 80s, 160s...
        delay = 10 * (2 ** (attempt.attempt_number - 1))
        next_attempt_number = attempt.attempt_number + 1
        
        # Create new attempt record for next time
        next_attempt = DeliveryAttempt(
            event_id=attempt.event_id,
            subscription_id=attempt.subscription_id,
            status="pending",
            attempt_number=next_attempt_number,
            scheduled_at=datetime.utcnow() + timedelta(seconds=delay)
        )
        db.add(next_attempt)
        await db.commit()
        await db.refresh(next_attempt)
        
        # Enqueue with delay
        await ctx['redis'].enqueue_job(
            'deliver_webhook', 
            str(next_attempt.id), 
            _defer_by=timedelta(seconds=delay)
        )

class WorkerSettings:
    functions = [dispatch_event, deliver_webhook]
    redis_settings = RedisSettings.from_dsn(os.getenv("REDIS_URL", "redis://redis:6379"))
    on_startup = None # Optional setup
