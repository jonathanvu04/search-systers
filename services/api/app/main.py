import sys
from pathlib import Path

# Add project root so services.embedding and services.ranking are findable
_root = Path(__file__).resolve().parents[3]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from fastapi import FastAPI

from .core.cors import setup_cors
from .routes import profiles, prompts, responses

app = FastAPI(title="search-systers API")
setup_cors(app)


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


app.include_router(profiles.router)
app.include_router(prompts.router)
app.include_router(responses.router)
