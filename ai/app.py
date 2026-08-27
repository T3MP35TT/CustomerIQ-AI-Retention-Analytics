import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from customeriq_qa import answer_question


# ============================================================
# CUSTOMERIQ — AI API
# ============================================================

app = FastAPI(
    title="CustomerIQ AI API",
    description="AI-powered customer intelligence and retention API",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODEL
# ============================================================

class QuestionRequest(BaseModel):
    question: str


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CustomerIQ AI API"
    }


# ============================================================
# AI QUESTION ENDPOINT
# ============================================================

@app.post("/ask")
def ask_customeriq(request: QuestionRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:

        answer = answer_question(question)

        return {
            "question": question,
            "answer": answer
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# SERVE FRONTEND
# ============================================================

FRONTEND_DIR = os.path.join(
    os.path.dirname(__file__),
    "frontend"
)

app.mount(
    "/",
    StaticFiles(
        directory=FRONTEND_DIR,
        html=True
    ),
    name="frontend"
)