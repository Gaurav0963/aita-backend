# 🧠 AITA --- Adaptive Intelligent Teaching Assistant Backend

AITA is a scalable, lab-aware AI Teaching Assistant backend built using:

-   ⚡ FastAPI (Fully Async)
-   🧠 LangGraph + LangChain
-   🚀 Groq LLMs (70B + 8B models)
-   📁 Structured HTML Lab Parsing
-   🗂 Centralized Path Management (pathlib)
-   📜 Custom Logging System
-   🔐 Rate Limiting (slowapi)

------------------------------------------------------------------------

# 🚀 Features

## ✅ Lab-Aware Context Injection

-   Extracts only the official problem statement from HTML.
-   Automatically detects which question a student is referring to.
-   Injects only relevant lab question into LLM.

## ✅ Fully Asynchronous Architecture

-   Uses async/await for LLM calls.
-   No thread-in-thread bottlenecks.
-   Scales efficiently under load.

## ✅ Structured Logging

Logs are saved in:

    logs/dd-mm-yy_hh-mm-ss.txt

## ✅ Modular Architecture

-   main.py → FastAPI entrypoint
-   ai_core.py → LLM + LangGraph logic
-   helper.py → HTML parsing
-   prompts.py → Persona + prompt templates
-   cache.py → In-memory lab cache
-   paths.py → Centralized filesystem paths
-   logger.py → Custom logging system

------------------------------------------------------------------------

# 📁 Project Structure

    aita-backend/
    │
    ├── main.py
    ├── ai_core.py
    ├── helper.py
    ├── prompts.py
    ├── cache.py
    ├── config.py
    ├── schemas.py
    ├── logger.py
    ├── paths.py
    │
    ├── logs/
    ├── labs/
    │   └── lab6.html
    │
    └── README.md

------------------------------------------------------------------------

# ⚙️ Installation

``` bash
conda create -n aita python=3.11 -y
conda activate aita
pip install -r requirements.txt
```

------------------------------------------------------------------------

# 🔐 Environment Variables

Create a `.env` file:

    GROQ_API_KEY=your_groq_api_key_here

------------------------------------------------------------------------

# ▶️ Running Locally

``` bash
uvicorn main:app --reload --port 5001
```

Open:

    http://127.0.0.1:5001/docs

------------------------------------------------------------------------

# 📊 Scaling Notes

⚠️ Current memory and caching are in-memory only.\
For 250+ students in production:

-   Replace MemorySaver with database checkpointing
-   Replace LAB_CACHE with Redis
-   Use multiple async workers (Gunicorn + UvicornWorker)

------------------------------------------------------------------------

# 🧾 Logging

Logs auto-save per server start with timestamped filenames.

------------------------------------------------------------------------

# 👨‍💻 Author

GAURAV --- M.Tech @ IIIT Bhagalpur\
Focused on Quantum ML, scalable LLM systems & AI architecture.

------------------------------------------------------------------------

# 📜 License

GNU GENERAL PUBLIC LICENSE
