from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, validator
import hashlib

class SurveySubmission(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=13, le=120)
    consent: bool = Field(..., description="Must be true to accept")
    rating: int = Field(..., ge=1, le=5)
    comments: Optional[str] = Field(None, max_length=1000)
    user_agent: Optional[str] = None
    submission_id: str

    @validator("comments")
    def _strip_comments(cls, v):
        return v.strip() if isinstance(v, str) else v

    @validator("consent")
    def _must_consent(cls, v):
        if v is not True:
            raise ValueError("consent must be true")
        return v
    
    def to_storable(self) -> dict:
        data = self.dict()
        # Hash PII fields before storage
        data["email"] = hashlib.sha256(self.email.encode("utf-8")).hexdigest()
        data["age"] = hashlib.sha256(str(self.age).encode("utf-8")).hexdigest()
        return data
        
#Good example of inheritance
class StoredSurveyRecord(SurveySubmission):
    received_at: datetime
    ip: str
    def to_storable(self) -> dict:
        data = self.dict()

        # Hash PII
        data["email"] = hashlib.sha256(self.email.encode("utf-8")).hexdigest()
        data["age"] = hashlib.sha256(str(self.age).encode("utf-8")).hexdigest()

        # Ensure submission_id exists
        if not data.get("submission_id"):
            hour_key = datetime.utcnow().strftime("%Y%m%d%H")
            raw = f"{self.email}{hour_key}"
            data["submission_id"] = hashlib.sha256(raw.encode("utf-8")).hexdigest()

        return data
