from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field

app = FastAPI()


class CandidateCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str = Field(pattern=r"^\d{11}$")

class Candidate(CandidateCreate):
    id: int


candidates = []


@app.post("/candidates")
def create_candidate(candidate: CandidateCreate):
    new_candidate = Candidate(
        id=len(candidates) + 1,
        **candidate.model_dump()
    )
    candidates.append(new_candidate)
    return new_candidate


@app.get("/candidates")
def get_candidates():
    return candidates


@app.get("/")
def root():
    return {"message": "Candidate Tracker API"}

@app.get("/candidates/{candidate_id}")
def get_candidate(candidate_id: int):
    for candidate in candidates:
        if candidate.id == candidate_id:
            return candidate

    raise HTTPException(status_code=404, detail="Candidate not found")

@app.put("/candidates/{candidate_id}")
def update_candidate(candidate_id: int, candidate: CandidateCreate):
    for index, existing_candidate in enumerate(candidates):
        if existing_candidate.id == candidate_id:
            updated_candidate = Candidate(
                id=candidate_id,
                **candidate.model_dump()
            )
            candidates[index] = updated_candidate
            return updated_candidate

    raise HTTPException(status_code=404, detail="Candidate not found")


@app.delete("/candidates/{candidate_id}")
def delete_candidate(candidate_id: int):
    for index, candidate in enumerate(candidates):
        if candidate.id == candidate_id:
            candidates.pop(index)
            return {"message": "Candidate deleted successfully"}

    raise HTTPException(status_code=404, detail="Candidate not found")