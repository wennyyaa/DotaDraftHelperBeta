from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .heroes import HERO_POOL
from .models import DraftRecommendation, DraftRequest, DraftResponse
from .services import draft_service  # stable service layer; hides rule vs ML engine details

app = FastAPI(title="Dota 2 Draft Helper API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/predict", response_model=DraftResponse)
def predict(payload: DraftRequest) -> DraftResponse:
    """Return the top 5 draft recommendations for the given matchup."""

    recs = draft_service.get_draft_recommendations(
        payload.allies, payload.enemies, k=12
    )

    recommended = [DraftRecommendation(**rec) for rec in recs]

    return DraftResponse(recommended=recommended)


@app.get("/heroes")
def list_heroes() -> dict:
    """Return the full hero pool used by the draft engine."""

    return {"heroes": list(HERO_POOL)}

