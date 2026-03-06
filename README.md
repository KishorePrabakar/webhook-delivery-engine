# Webhook Delivery & Event Routing platform Engine

A high-throughput, asynchronous webhook delivery platform built with FastAPI, Redis, and React. This project demonstrates a production-grade architecture for reliable event distribution, featuring exponential backoff, request signing (HMAC), and real-time observability.

## 🚀 Key Features

- **Asynchronous Ingestion**: FastAPI endpoints designed for sub-millisecond response times by offloading processing to background workers.
- **Reliable Delivery Engine**: Powered by `arq` (Redis-based), supporting distributed task execution and failure isolation.
- **Exponential Backoff**: Advanced retry logic with jitter to prevent destination server overload during outages.
- **HMAC-SHA256 Security**: Every outgoing request is signed with a unique secret per subscription, protecting against spoofing and replay attacks.
- **Real-time Monitoring**: Real-time delivery tracking via WebSockets on a modern React dashboard.
- **Dead Letter Queue (DLQ)**: Comprehensive failure handling—messages that exceed maximum retries are moved to a DLQ for review.

## 🛠 Tech Stack

- **Backend**: Python, FastAPI
- **Database**: PostgreSQL (SQLAlchemy Async)
- **Workers**: Redis, Arq
- **Frontend**: React, Tailwind CSS, Vite
- **Infrastructure**: Docker, Docker Compose

## 🏗 Architecture Overview

1. **Ingestion**: An external service sends an event to `/api/v1/events`.
2. **Fan-out**: The backend pushes the event ID to Redis. A worker identifies all subscriptions matching the event type.
3. **Dispatch**: For each subscriber, a new task is enqueued with a unique `DeliveryAttempt` ID.
4. **Delivery**: The worker performs an HTTP POST to the target URL, including the HMAC signature in the headers.
5. **Recovery**: If the delivery fails, the worker calculates the next retry time using an exponential formula and re-schedules the task.
6. **Observability**: Every status change is broadcasted via WebSockets to the connected dashboard.

## 🏁 Getting Started

### Prerequisites
- Docker & Docker Compose

### Launch the Platform
```bash
docker-compose up --build
```
The services will be available at:
- **Backend API**: `http://localhost:8000`
- **Dashboard**: `http://localhost:5173` (once deps are installed locally)

## 🔒 Security: HMAC Signing

Each webhook target receives a header `X-Webhook-Signature` formatted as `t=<timestamp>,v1=<signature>`.
Validation logic:
1. Concatenate `timestamp` and `payload_json`.
2. Compute `HMAC-SHA256` using the shared secret.
3. Compare with the provided signature to ensure data integrity.

---
*Created for portfolio demonstration. Optimized for scalability and reliability.*
