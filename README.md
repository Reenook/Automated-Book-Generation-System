# Automated AI Book Generation System

A modular and scalable backend system built to automate the creation of high-quality books. This system implements human-in-the-loop gating, recursive context chaining, and automated workflow branching using FastAPI, Supabase, and OpenAI.

## Objective
The system is designed to handle the complexity of long-form content generation by ensuring that each chapter maintains narrative consistency through "Context Chaining" while allowing editors to review and approve content at every critical stage.

## Tech Stack
- **Automation Engine:** Python / FastAPI
- **Input Source:** Google Sheets (via Service Account)
- **Database:** Supabase (PostgreSQL)
- **AI Model:** OpenAI GPT-4o-mini
- **Notifications:** Email (SMTP)
- **Output Format:** Microsoft Word (.docx)

## .env variables
```text
GOOGLE_SERVICE_ACCOUNT_JSON='{"type": "service_account", "project_id": "...", "private_key_id": "...", "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n", "client_email": "...", "client_id": "...", "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.google.com/token", "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs", "client_x509_cert_url": "..."}'
GOOGLE_SHEET_NAME="Your Spreadsheet Name Here"

# Supabase Configuration
SUPABASE_URL="https://your-project-id.supabase.co"
SUPABASE_KEY="your-supabase-key"

# AI Model Configuration
OPENAI_API_KEY="your-openai-key"

# SMTP Notification Configuration
EMAIL_SENDER="your-email@gmail.com"
EMAIL_PASSWORD="your-16-character-app-password"
```

## Key Architectural Features

### 1. Google Sheets Input Source
The system uses a background worker (`sheets_trigger.py`) that polls a Google Sheet every 30 seconds. It detects new rows where `Automation_Status` is empty, triggers the Stage 1 Outline via FastAPI, and marks the row as `Processed`.

### 2. Conditional Gating Logic (Human-in-the-Loop)
The system is designed to "pause" between stages:
- **Outline Gate:** The system generates an outline but refuses to write chapters until `status_outline_notes` is manually set to `no_notes_needed` in Supabase.
- **Compilation Gate:** The final book is only compiled and emailed once the `final_review_notes_status` is cleared by the editor.

### 3. Recursive Context Chaining
To maintain narrative consistency:
1. Before generating Chapter N, the system fetches all previous chapter summaries (1 to N-1) from Supabase.
2. It injects these summaries into the prompt as `context_input`.
3. This ensures the AI maintains character arcs and plot points without exceeding token limits.

### 4. Asynchronous Background Tasks
Chapter generation uses FastAPI's `BackgroundTasks` to trigger the generation loop, allowing the API to remain responsive while the AI works in the background.

## Project Structure
```text
.
├── main.py              # FastAPI routes and Gating Logic
├── services.py          # AI Logic, Context Chaining & Document Generation
├── sheets_trigger.py    # Google Sheets Polling Worker
├── database.py          # Supabase client configuration
├── models.py            # Pydantic schemas
├── notifications.py     # SMTP Email logic
└── .env                 # Environment variables
```


