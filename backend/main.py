from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models import DraftRecommendation, DraftRequest, DraftResponse, DraftIdentity
from .services.draft_identity import build_draft_identity



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


    recs = draft_service.get_draft_recommendations(
    payload.allies,
    payload.enemies,
    k=8,
    target_role=payload.target_role,
    occupied_roles=payload.occupied_roles,
)
    recommended = [DraftRecommendation(**rec) for rec in recs]
    identity = DraftIdentity(**build_draft_identity(payload.allies))

    return DraftResponse(
        recommended=recommended,
        identity=identity,
    )


@app.get("/heroes")
def list_heroes() -> dict:
    """Return the full hero pool used by the draft engine."""

    return {"heroes": list(HERO_POOL)}

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://localhost:5176",
        "http://127.0.0.1:5176",
        "http://localhost:5177",
        "http://127.0.0.1:5177",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)