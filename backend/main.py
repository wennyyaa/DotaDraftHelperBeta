from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models import DraftRecommendation, DraftRequest, DraftResponse, DraftIdentity
from .services.draft_identity import analyze_draft_identity
from .services.draft_needs import analyze_draft_needs




from .heroes import HERO_POOL
from .models import DraftRecommendation, DraftRequest, DraftResponse
from .services import draft_service  # stable service layer; hides rule vs ML engine details
from fastapi.middleware.cors import CORSMiddleware



ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "https://dota-draft-helper-beta.vercel.app",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
),





def infer_target_role_from_ally_slots(ally_slots) -> str | None:
    if not ally_slots:
        return None

    data = ally_slots.model_dump()
    missing = [role for role, hero in data.items() if not hero]
    filled = [role for role, hero in data.items() if hero]

    if len(missing) == 1 and len(filled) >= 3:
        return missing[0]

    return None


@app.post("/predict", response_model=DraftResponse)
def predict(payload: DraftRequest) -> DraftResponse:
    
    draft_needs = analyze_draft_needs(payload.allies)


    effective_target_role = payload.target_role or infer_target_role_from_ally_slots(
    payload.ally_slots
)

    recs = draft_service.get_draft_recommendations(
    payload.allies,
    payload.enemies,
    k=8,
    target_role=effective_target_role,
    occupied_roles=payload.occupied_roles,
    ally_slots=payload.ally_slots,
)
    
    
    recommended = [DraftRecommendation(**rec) for rec in recs]
    identity = DraftIdentity(**analyze_draft_identity(payload.allies))

    return DraftResponse(
        recommended=recommended,
        identity=identity,
        draft_needs= draft_needs,
    )


@app.get("/heroes")
def list_heroes() -> dict:


    return {"heroes": list(HERO_POOL)}

