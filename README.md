# Ai Solutions

A simple FastAPI service providing endpoints for order management, item lookups and conversational intent detection.

## Project Overview

This project exposes REST APIs that allow clients to manage orders and items and also offers a small Hebrew intent detection utility. A Redis based chat memory router is included for temporary chat state storage. The service uses a MySQL database accessed via SQLAlchemy.

## Tech Stack

- **Python 3**
- **FastAPI** for the web framework
- **SQLAlchemy** with **MySQL** for persistent storage
- **Redis** for chat memory features
- **Pydantic** for data validation
- **Uvicorn** as the ASGI server

## Running the API

Install all dependencies and launch the server using `uvicorn` (the `start.sh` script contains the command):

```bash
pip install -r requirements.txt
bash start.sh
```

The application will start on `http://127.0.0.1:8000/` with automatic reload enabled. The root endpoint returns a welcome message:

```bash
curl http://127.0.0.1:8000/
```

```json
{"message": "Welcome to Ai Solutions"}
```

## Running Tests

Pytest is used for the test suite. Install the dependencies and then run:

```bash
pip install -r requirements.txt
pytest -q
```

## Repository Layout

- `main.py` – FastAPI application with router registration and the root endpoint
- `Routers/` – Order, item, customer and intent API routes
- `DB/` – Database models and helper functions using SQLAlchemy and Redis
- `intent_logic/` – Intent detection logic
- `utils/` – Utility helpers and Pydantic models
- `Tests/` – Pytest tests covering endpoints and helper functions

---

Feel free to fork this repository and adapt it to your needs.
