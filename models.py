from pydantic import BaseModel
from typing import Optional

class ProjectCreate(BaseModel):
    title: str
    initial_notes: str

class ChapterUpdate(BaseModel):
    notes: Optional[str] = None
    status: str  # e.g., "approved", "needs_revision"