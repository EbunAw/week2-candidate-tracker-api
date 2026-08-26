from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Candidate as CandidateModel, Application as ApplicationModel
from schemas import (
    CandidateCreate,
    CandidateResponse,
    ApplicationCreate,
    ApplicationResponse,
)
app = FastAPI()


@app.post("/candidates", response_model=CandidateResponse)
def create_candidate(candidate: CandidateCreate, db: Session = Depends(get_db)):
    new_candidate = CandidateModel(
        name=candidate.name,
        email=candidate.email,
        phone=candidate.phone
    )

    db.add(new_candidate)
    db.commit()
    db.refresh(new_candidate)

    return new_candidate

@app.get("/candidates", response_model=list[CandidateResponse])
def get_candidates(db: Session = Depends(get_db)):
    return db.query(CandidateModel).all()

@app.post("/applications", response_model=ApplicationResponse)
def create_application(
    application: ApplicationCreate,
    db: Session = Depends(get_db)
):
    candidate = db.get(CandidateModel, application.candidate_id)

    if candidate is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    new_application = ApplicationModel(
        candidate_id=application.candidate_id,
        position=application.position,
        status=application.status
    )

    db.add(new_application)
    db.commit()
    db.refresh(new_application)

    return new_application


@app.get("/applications/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: int,
    db: Session = Depends(get_db)
):
    application = db.get(ApplicationModel, application_id)

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    return application


@app.get("/")
def root():
    return {"message": "Candidate Tracker API"}

@app.get("/candidates/{candidate_id}", response_model=CandidateResponse)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.get(CandidateModel, candidate_id)

    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")

    return candidate

@app.put("/candidates/{candidate_id}", response_model=CandidateResponse)
def update_candidate(
    candidate_id: int,
    candidate: CandidateCreate,
    db: Session = Depends(get_db)
):
    existing_candidate = db.get(CandidateModel, candidate_id)

    if existing_candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")

    existing_candidate.name = candidate.name
    existing_candidate.email = candidate.email
    existing_candidate.phone = candidate.phone

    db.commit()
    db.refresh(existing_candidate)

    return existing_candidate


@app.delete("/candidates/{candidate_id}")
def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.get(CandidateModel, candidate_id)

    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")

    db.delete(candidate)
    db.commit()

    return {"message": "Candidate deleted successfully"}