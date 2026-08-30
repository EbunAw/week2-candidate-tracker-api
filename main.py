import time
import uuid
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from auth import (
    check_login_rate_limit,
    create_access_token,
    get_current_user,
    hash_password,
    record_failed_login,
    reset_failed_logins,
    verify_password,
)
from database import get_db
from logging_config import logger
from models import (
    Application as ApplicationModel,
    Candidate as CandidateModel,
    User as UserModel,
)
from schemas import (
    ApplicationCreate,
    ApplicationResponse,
    CandidateCreate,
    CandidateResponse,
    Token,
    UserCreate,
    UserResponse,
)

app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.perf_counter()

    response = await call_next(request)

    latency_ms = round(
        (time.perf_counter() - start_time) * 1000,
        2,
    )

    logger.info(
        "request completed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "latency_ms": latency_ms,
        },
    )

    response.headers["X-Request-ID"] = request_id

    return response


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred."
        }
    )

@app.post("/candidates", response_model=CandidateResponse)
def create_candidate(
    candidate: CandidateCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
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
def get_candidates(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(CandidateModel).all()


@app.get("/candidates/{candidate_id}", response_model=CandidateResponse)
def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    candidate = db.get(CandidateModel, candidate_id)

    if candidate is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    return candidate


@app.put("/candidates/{candidate_id}", response_model=CandidateResponse)
def update_candidate(
    candidate_id: int,
    candidate: CandidateCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    existing_candidate = db.get(CandidateModel, candidate_id)

    if existing_candidate is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    existing_candidate.name = candidate.name
    existing_candidate.email = candidate.email
    existing_candidate.phone = candidate.phone

    db.commit()
    db.refresh(existing_candidate)

    return existing_candidate


@app.delete("/candidates/{candidate_id}")
def delete_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    candidate = db.get(CandidateModel, candidate_id)

    if candidate is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    db.delete(candidate)
    db.commit()

    return {"message": "Candidate deleted successfully"}


@app.post("/applications", response_model=ApplicationResponse)
def create_application(
    application: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
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


@app.get(
    "/applications/{application_id}",
    response_model=ApplicationResponse
)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    application = db.get(ApplicationModel, application_id)

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    return application


@app.post("/register", response_model=UserResponse)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(UserModel).filter(
        UserModel.username == user.username
    ).first()

    if existing_user is not None:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    new_user = UserModel(
        username=user.username,
        password_hash=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.post("/login", response_model=Token)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    username = form_data.username

    if not check_login_rate_limit(username):
        raise HTTPException(
            status_code=429,
            detail="Too many login attempts. Please try again later."
        )

    existing_user = db.query(UserModel).filter(
        UserModel.username == username
    ).first()

    if existing_user is None:
        record_failed_login(username)

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not verify_password(
        form_data.password,
        existing_user.password_hash
    ):
        record_failed_login(username)

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    reset_failed_logins(username)

    access_token = create_access_token(existing_user.username)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.get("/")
def root():
    return {"message": "Candidate Tracker API"}