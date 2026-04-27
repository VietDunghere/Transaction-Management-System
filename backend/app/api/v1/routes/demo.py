from __future__ import annotations
"""
Router: Demo Runner
POST /demo/start   — start demo data generation (OPERATOR)
POST /demo/stop    — stop running demo (OPERATOR)
GET  /demo/status  — current demo state + recent events (OPERATOR)
"""

from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from app.api.v1.deps import require_roles
from app.schemas.auth import TokenPayload
from app.schemas.demo import DemoStartRequest, DemoStatusResponse
from app.services.demo_runner_service import DemoAlreadyRunningError, DemoRunnerService

router = APIRouter(prefix="/demo", tags=["Demo Runner"])


def _get_runner() -> DemoRunnerService:
    return DemoRunnerService.get_instance()


@router.post(
    "/start",
    response_model=DemoStatusResponse,
    summary="Start demo data generation",
    description="Spawns a background task that generates fake transactions and loans. Only one demo can run at a time.",
)
async def start_demo(
    body: DemoStartRequest,
    token: TokenPayload = Depends(require_roles("OPERATOR")),
) -> DemoStatusResponse | JSONResponse:
    runner = _get_runner()
    try:
        return await runner.start(body, user_id=token.sub, username=token.full_name or "operator")
    except DemoAlreadyRunningError as exc:
        return JSONResponse(
            status_code=409,
            content={"code": "DEMO_ALREADY_RUNNING", "message": str(exc)},
        )


@router.post(
    "/stop",
    response_model=DemoStatusResponse,
    summary="Stop running demo",
)
async def stop_demo(
    token: TokenPayload = Depends(require_roles("OPERATOR")),
) -> DemoStatusResponse:
    runner = _get_runner()
    return await runner.stop()


@router.get(
    "/status",
    response_model=DemoStatusResponse,
    summary="Get demo runner status",
    description="Returns current state, stats, and last 50 events. Frontend polls this at 1s interval.",
)
async def demo_status(
    token: TokenPayload = Depends(require_roles("OPERATOR", "ANALYST", "MANAGER", "REVIEWER", "ADMIN")),
) -> DemoStatusResponse:
    runner = _get_runner()
    return runner.status()
