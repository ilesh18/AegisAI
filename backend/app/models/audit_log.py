"""
AISystemAuditLog model — records every field change on an AISystem row.
Copyright (C) 2024 Sarthak Doshi (github.com/SdSarthak)
SPDX-License-Identifier: AGPL-3.0-only

TODO for contributors (help wanted):
  - Wire this model via a SQLAlchemy `event.listen` on AISystem's `after_update`
    event (see: https://docs.sqlalchemy.org/en/20/orm/events.html#sqlalchemy.orm.events.InstanceEvents.after_update).
  - Capture old_values and new_values by comparing the history of each column
    using `sqlalchemy.orm.attributes.get_history`.
  - Add a GET /api/v1/ai-systems/{id}/history endpoint that returns paginated
    log entries for a given system.
  - Acceptance criteria: updating a system's name via PATCH is reflected as a
    new row in ai_system_audit_logs with correct old/new values.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class AISystemAuditLog(Base):
    __tablename__ = "ai_system_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    ai_system_id = Column(Integer, ForeignKey("ai_systems.id"), nullable=False)
    changed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # JSON dicts of {field: value} before and after the change
    old_values = Column(JSON, default=dict)
    new_values = Column(JSON, default=dict)

    changed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    ai_system = relationship("AISystem")
    changed_by = relationship("User")
