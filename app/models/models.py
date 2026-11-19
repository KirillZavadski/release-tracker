from datetime import datetime, UTC
from typing import Optional, List
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.enums import Status_variable as statuses

db = SQLAlchemy()

class Service(db.Model):
    __tablename__ = 'services'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    repository_url: Mapped[Optional[str]] = mapped_column(String(200))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    releases: Mapped[List['Release']] = relationship(
                                                    'Release',
                                                    backref='service', 
                                                    cascade='all, delete-orphan',
                                                    lazy=True
                                                    )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'repository_url': self.repository_url
        }

class Release(db.Model):
    __tablename__ = 'releases'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    version: Mapped[str] = mapped_column(String(50))
    changelog: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[statuses] = mapped_column(
        db.Enum(statuses),
        default=statuses.DRAFT,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(UTC))
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    service_id: Mapped[int] = mapped_column(ForeignKey('services.id', ondelete='CASCADE'))

    @property
    def is_deadline_reached(self) -> bool:
        if self.status != statuses.TESTING or self.deadline is None:
            return False
        now = datetime.now(UTC) if self.deadline.tzinfo else datetime.now()
        return now >= self.deadline

    def to_dict(self) -> dict:
        status_value = self.status.value if isinstance(self.status, statuses) else self.status
        return {
            'id': self.id,
            'version': self.version,
            'changelog': self.changelog,
            'status': self.status,
            'deadline': self.deadline.strftime('%d.%m.%Y %H:%M') if self.deadline else None,
            'deadline_iso': self.deadline.strftime('%Y-%m-%dT%H:%M') if self.deadline else None,
            'deadline_reached': self.is_deadline_reached,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'service_id': self.service_id,
        }