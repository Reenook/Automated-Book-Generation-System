#  Automated AI Book Generation System

A modular and scalable backend system built to automate the creation of high-quality books. This system implements **human-in-the-loop gating**, **recursive context chaining**, and **automated workflow branching** using FastAPI, Supabase, and OpenAI.

##  Objective
The system is designed to handle the complexity of long-form content generation by ensuring that each chapter maintains narrative consistency through "Context Chaining" while allowing editors to review and approve content at every critical stage.

##  Tech Stack
- **Automation Engine:** Python / FastAPI
- **Database:** Supabase (PostgreSQL)
- **AI Model:** OpenAI GPT-4o-mini
- **Notifications:** Email (SMTP)
- **Output Format:** Microsoft Word (.docx)

##  Key Architectural Features

### 1. Conditional Gating Logic (Human-in-the-Loop)
The system is designed to "pause" between stages. 
- **Outline Gate:** The system generates an outline but refuses to write chapters until the `status_outline_notes` is manually set to `no_notes_needed` in Supabase.
- **Compilation Gate:** The final book is only compiled and emailed once the `final_review_notes_status` is cleared by the editor.

### 2. Recursive Context Chaining
To solve the "memory loss" issue in long AI generations, this system implements recursive context. Before generating Chapter N, the system:
1. Fetches all previous chapter summaries (1 to N-1) from Supabase.
2. Injects these summaries into the prompt as `context_input`.
3. Generates the new chapter based on the accumulated narrative history.

### 3. Asynchronous Background Tasks
Chapter generation is a heavy process. The system utilizes FastAPI's `BackgroundTasks` to trigger the generation loop, allowing the API to remain responsive while the AI works in the background.

##  Project Structure
```text
.
├── main.py              # FastAPI routes and Gating Logic
├── services.py          # AI Logic, Context Chaining & PDF to email
├── database.py          # Supabase client configuration
├── models.py            # schemas 
├── notifications.py     # Notifications to email using SMTP
└── .env                 # Environment variables (API Keys, SMTP)