from pydantic import BaseModel, EmailStr, Field


class CandidateCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str = Field(pattern=r"^(070|071|080|081|090|091)\d{8}$")


class CandidateResponse(CandidateCreate):
    id: int

    class Config:
        from_attributes = True