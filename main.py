from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field

app = FastAPI()


class CandidateCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str = Field(pattern=r"^(070|071|080|081|090|091)\d{8}$")

class Candidate(CandidateCreate):
    id: int


candidates = []
next_candidate_id = 1


@app.post("/candidates")
def create_candidate(candidate: CandidateCreate):
    global next_candidate_id

    new_candidate = Candidate(
        id=next_candidate_id,
        **candidate.model_dump()
    )

    candidates.append(new_candidate)
    next_candidate_id += 1

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