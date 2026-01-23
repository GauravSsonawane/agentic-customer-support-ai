# 🚀 How to Run the Agentic Customer Support AI

This guide will help you start the application (Backend + Frontend) on your local machine.

## ✅ Prerequisites

1.  **Ollama** (Required for the AI models)
    *   Download and install from [ollama.com](https://ollama.com).
    *   Run `ollama serve` in a terminal.
    *   Pull the model: `ollama pull llama3.1` (or the model specified in your `.env`).

2.  **Docker Desktop** (Recommended)
    *   Ensure it is installed and running.

---

## 🐳 Option 1: Run with Docker (Easiest)

This method automatically handles all dependencies and configuration.

1.  **Open a terminal** in the project folder.
2.  **Run the command:**
    ```powershell
    docker compose up --build
    ```
3.  **Wait** for the build to finish. Once you see "Application startup complete", open your browser:
    *   **Frontend (Chat UI)**: [http://localhost:8501](http://localhost:8501)
    *   **Backend API**: [http://localhost:8070/docs](http://localhost:8070/docs)

**Stopping the App:**
Press `Ctrl+C` in the terminal or run `docker compose down`.

---

## 🐍 Option 2: Run Manually (Python)

If you prefer to run it without Docker, follow these steps.

### 1. Setup Environment
```powershell
# Create virtual environment
python -m venv venv

# Activate it (Windows)
.\venv\Scripts\activate

# Install dependencies (use the clean requirements file)
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Ensure your `.env` file looks like this (for local run, `localhost` works fine for Ollama):
```ini
LANGCHAIN_API_KEY=your_key_here
OLLAMA_BASE_URL=http://localhost:11434
```
*(Note: In Docker, we use `host.docker.internal`, but for local Python, `localhost` is correct).*

### 3. Start the Backend
Open a new terminal, activate venv, and run:
```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8070 --reload
```
*Backend is now running at `http://localhost:8070`*

### 4. Start the Frontend
Open another terminal, activate venv, and run:
```powershell
# Windows PowerShell
$env:API_URL="http://localhost:8070/query"; streamlit run ui/app.py
```
*Frontend is now running at `http://localhost:8501`*

---

## 🛠️ Troubleshooting

**"Error while processing request" or Connection Error:**
*   Ensure **Ollama** is running (`ollama serve`).
*   If running in Docker, ensure `.env` has `OLLAMA_BASE_URL=http://host.docker.internal:11434`.
*   If running Manually, ensure `.env` has `OLLAMA_BASE_URL=http://localhost:11434`.

**Port Conflicts:**
*   If port `8070` is busy, change it in `docker-compose.yml` and `.env`.
