"""
Public Compliance Badge API — no authentication required.
Copyright (C) 2024 Sarthak Doshi (github.com/SdSarthak)
SPDX-License-Identifier: AGPL-3.0-only

TODO for contributors (help wanted):
  - Implement GET /badge/{system_id} — return an SVG badge showing the
    AI system's current compliance status and risk level.
    This endpoint is PUBLIC (no JWT required) so organisations can embed
    the badge in their README or website.
  - The badge should show: system name, risk level, compliance status,
    and a color (green=compliant, yellow=in_progress, red=non_compliant).
  - Optionally support ?format=json to return machine-readable JSON instead.
  - Acceptance criteria: visiting /badge/{id} in a browser renders an
    SVG badge without requiring a login.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.core.database import get_db

router = APIRouter()


@router.get("/{system_id}", tags=["Compliance Badge"])
def get_compliance_badge(
    system_id: int,
    format: str = "svg",      # "svg" | "json"
    db: Session = Depends(get_db),
):
    """
    Return a public compliance badge for an AI system.

    TODO (help wanted): look up the AISystem by ID (no auth check — public),
    generate an SVG from the badge template in
    app/modules/badge/badge_generator.py, return with Content-Type image/svg+xml.
    Return 404 if the system does not exist.
    """
    # TODO: implement
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")
