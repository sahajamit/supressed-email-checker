from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class EmailCheckRequest(BaseModel):
    email: EmailStr

class SuppressionInfo(BaseModel):
    email_address: str
    reason: str
    last_update_time: str

class EmailCheckResponse(BaseModel):
    email: str
    is_suppressed: bool
    reason: Optional[str] = None
    last_update_time: Optional[str] = None
    human_readable_explanation: Optional[str] = None
