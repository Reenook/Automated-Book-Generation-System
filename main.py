from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from database import supabase
import services

app = FastAPI(title="AI Book Generation System")


# Models for Swagger Input
class ProjectCreate(BaseModel):
    title: str
    initial_notes: str


@app.post("/projects/1-generate-outline", tags=["Stage 1: Input & Outline"])
async def create_outline(data: ProjectCreate):
    """
    Requirement: Takes title/notes and stores outline in DB for review.
    """
    # 1. Generate Outline
    outline = services.generate_outline(data.title, data.initial_notes)

    # 2. Store in Supabase with 'yes' status (Gating enabled)
    res = supabase.table("projects").insert({
        "title": data.title,
        "notes_on_outline_before": data.initial_notes,
        "outline": outline,
        "status_outline_notes": "yes"
    }).execute()

    return {"project_id": res.data[0]['id'], "outline": outline, "status": "Waiting for Editor Approval"}


# Change this line in your approve_and_generate function
@app.post("/projects/2-approve-and-generate", tags=["Stage 2: Gating & Chapters"])
async def approve_and_generate(project_id: str, background_tasks: BackgroundTasks):
    # 1. Check Gating Status
    proj = supabase.table("projects").select("status_outline_notes").eq("id", project_id).single().execute()

    if proj.data["status_outline_notes"] != "no_notes_needed":
        raise HTTPException(
            status_code=400,
            detail="GATING ERROR: You must manually set 'status_outline_notes' to 'no_notes_needed' in Supabase to proceed."
        )

    # 2. TRIGGER THE CORRECT SERVICE FUNCTION
    # Use services.run_full_generation instead of the local run_chapter_workflow
    background_tasks.add_task(services.run_full_generation, project_id)

    return {"message": "Gating passed. Recursive Chapter generation started."}


async def run_chapter_workflow(p_id: str):
    """
    Requirement: Context Chaining (Summaries of Ch 1 to N-1).
    """
    # For the demo, we'll generate 3 chapters
    chapters = ["Introduction", "The Deep Dive", "The Conclusion"]

    for i, title in enumerate(chapters):
        ch_num = i + 1
        # generate_chapter fetches previous summaries for context
        result = services.generate_chapter(p_id, ch_num, title)

        supabase.table("chapters").insert({
            "project_id": p_id,
            "chapter_number": ch_num,
            "title": title,
            "content": result["content"],
            "summary": result["summary"]
        }).execute()


@app.get("/projects/3-export", tags=["Stage 3: Compilation"])
async def export_book(project_id: str):
    """
    Requirement: Final Compilation Stage.
    """
    path = services.compile_final_book(project_id)

    if not path:
        raise HTTPException(
            status_code=400,
            detail="Final draft is paused. Please set 'final_review_notes_status' to 'no_notes_needed' in Supabase[cite: 61, 64]."
        )

    return {"download_path": path, "status": "Final draft compiled and emailed[cite: 71]."}