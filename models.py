# models.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class ProfessorModel(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    university: str
    department: Optional[str] = None
    research_area: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None
