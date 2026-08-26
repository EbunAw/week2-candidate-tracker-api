from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CandidateCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str = Field(pattern=r"^(070|071|080|081|090|091)\d{8}$")


class CandidateResponse(CandidateCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ApplicationCreate(BaseModel):
    candidate_id: int
    position: str
    status: str


class ApplicationResponse(ApplicationCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)