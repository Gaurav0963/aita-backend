# 🤖 AITA Backend — Production Architecture

AI Teaching Assistant (AITA) backend built with **FastAPI**, **PostgreSQL**, and **Groq LLMs**, designed to scale for 250+ concurrent students.

## 🌐 Deployment Architecture

* **Frontend:** Firebase Hosting

* **Backend:** Render (FastAPI + Uvicorn)

* **Database:** Render PostgreSQL

* **LLM Provider:** Groq (LLaMA models)

The system is:

* Fully asynchronous (`asyncpg`, `httpx`, `ainvoke`)

* Horizontally scalable

* Database-backed (no in-memory session loss during server restarts)

* Cloud-safe (Render loads balancer compatible)

* Lab-aware (auto-fetch + smart caching)

## 🔑 Environment Variables

To run this project, you must create a `.env` file in the root directory.

```env
# Your Groq API Key (Required for LLaMA models)
GROQ_API_KEY="gsk_your_api_key_here"

# Your PostgreSQL Connection String
# Local Example: postgresql://postgres:password@localhost:5432/aita_db
# Render Example: postgresql://user:pass@host/db
DATABASE_URL="postgresql://..."
```


## 📦 Project Structure

```Plaintext
aita-backend/
│
├── main.py        # FastAPI entry point, routes, rate limiting
├── ai_core.py     # AI orchestration, cache management, routing
├── helper.py      # Network fetching & HTML parsing (BeautifulSoup)
├── prompts.py     # Centralized LLM system prompts
├── memory.py      # DB interaction for thread persistence
├── database.py    # Async SQLAlchemy engine configuration
├── config.py      # LLM initialization
├── logger.py      # Cloud-native standard output logging
├── schemas.py     # Pydantic data validation models
└── requirements.txt
```

## 🚀 Lab Context Flow (How it reads assignments)

Frontend sends the active lab identifier dynamically:
```JavaScript
lab_id = LATEST_LAB_LINK.replace(".html", "")
```

Backend (ai_core.py):

    - Checks RAM Cache (LAB_CACHE)
    - If missing, fetches lab HTML from Firebase via httpx
    - Extracts .lab-question-data and cleans HTML noise via a small LLM
    - Caches the cleaned result permanently
    - Injects the relevant question directly into the AITA System Prompt
    - Context is successfully reused across all students without spamming Firebase.

## 📊 Complete Production Flow & Bottlenecks

Because the application is heavily optimized for asynchronous I/O, the FastAPI server can smoothly juggle hundreds of concurrent student requests while waiting for external services.

### Visual Production Flow:

```Plaintext
┌─────────────────────────────┐
│          STUDENT UI         │
│  (Firebase Hosted Frontend) │
└──────────────┬──────────────┘
               │ POST /chat
               ▼
┌─────────────────────────────┐
│      FastAPI Backend        │
│     (Render Deployment)     │
└──────────────┬──────────────┘
               │
               ├──────────────► PostgreSQL
               │                  (Conversation Memory)
               │
               ├──────────────► LAB_CACHE (RAM)
               │                 │
               │                 └─ If miss:
               │                     └─ Fetch Firebase lab HTML
               │
               └──────────────► Groq LLM (Main Model)
                                   │
                                   ▼
                         Response Generated
                                   │
                                   ▼
                         Saved to PostgreSQL
                                   │
                                   ▼
                             Sent to Student
```


### Full Request Lifecycle Diagram:

```code
sequenceDiagram
    actor User
    participant UI as Frontend (React)
    participant API as FastAPI Backend
    participant DB as PostgreSQL
    participant Cache as LAB_CACHE
    participant FB as Firebase Hosting
    participant LLM as Groq (LLaMA)

    User->>UI: Types message & hits Send
    UI->>API: POST /chat {message, lab_id: "lab6"}
    activate API
    
    API->>DB: Load conversation history
    DB-->>API: Return history
    
    API->>Cache: Check for "lab6"
    alt If Miss (Not Cached)
        API->>FB: Fetch lab6.html
        FB-->>API: Return HTML
        API->>API: Parse .lab-question-data
        API->>LLM: Clean using small LLM
        LLM-->>API: Cleaned text
        API->>Cache: Store cleaned questions
    end
    Cache-->>API: Return cleaned questions

    API->>LLM: Select relevant question (Small LLM)
    LLM-->>API: Question ID
    
    API->>API: Build final prompt (Persona + Context + History)
    
    API->>LLM: Generate response (main_llm.ainvoke)
    LLM-->>API: Final Reply
    
    API->>DB: Save updated conversation
    DB-->>API: Confirm save
    
    API-->>UI: Return response JSON
    deactivate API
    
    UI-->>User: UI updates chat window
```

### Request Lifecycle Steps:

1. User types message
2. handleSend() triggers
3. Frontend sends payload with lab_id
4. FastAPI /chat endpoint receives request
5. Backend loads conversation history from PostgreSQL
6. Backend calls get_clean_lab_questions("lab6")

    * If cached → return immediately
    * If not cached: Fetch lab6.html from Firebase, parse .lab-question-data, clean using small LLM, and store in LAB_CACHE.

7. Backend selects relevant question using routing LLM
8. Backend builds final system prompt: BASE_PERSONA + Lab Question Context + Previous Conversation
9. main_llm.ainvoke(messages) generates response
10. Backend saves new messages to PostgreSQL
11. Response returned to frontend
12. UI updates

### Visual Bottleneck Chart:
```Plaintext
LLM Inference    ████████████████████████████ 70%
Network          ████ 10%
Small LLM        ███ 8%
Database         ██ 5%
Other            █ 2%
```

## ⚡ Horizontal Scaling & Production Deployment

Render Start Command:
```bash
uvicorn main:app --host 0.0.0.0 --port 10000 --proxy-headers --forwarded-allow-ips="*"
```

Ensures:

    * Real client IP detection (bypassing Render's Load Balancer IP)

    * Safe and accurate SlowAPI rate limiting (30 req/min per student)

    * Stateless multi-worker compatibility

## 🛡 Production Safety Checklist

* [x] Async FastAPI

* [x] Async PostgreSQL (asyncpg)

* [x] DB-backed memory

* [x] Smart lab caching (Prevents Firebase DDoS)

* [x] No local file dependency (httpx network fetch)

* [x] Proxy headers enabled

* [x] DB Connection Pool strict limits (pool_size=2)


## 🧩 Local Development Setup

1. Create Virtual Environment
```bash
conda create -n aita python=3.11 -y
conda activate aita
```

2. Install Dependencies
```bash
pip install -r requirements.txt
```

3. Start PostgreSQL
```Plaintext
Ensure you have a local PostgreSQL database running and update your .env file with the connection string. On first startup, SQLAlchemy will automatically build the conversations table.
```

4. Run the Server
```bash
uvicorn main:app --reload --port 5001
```

## 🧪 Interactive API Documentation

Because this is built on FastAPI, you do not need the React frontend to test the bot locally. Once the server is running, navigate to:

👉 https://www.google.com/search?q=http://127.0.0.1:5001/docs

This provides a fully interactive Swagger UI where you can easily send mock JSON payloads to the /chat endpoint and watch the LLM respond in real time.