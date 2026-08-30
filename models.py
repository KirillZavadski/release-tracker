from datetime import datetime, UTC
from typing import Optional, List
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

class Service(db.Model):
    __tablename__ = 'services'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    repository_url: Mapped[Optional[str]] = mapped_column(String(200))
    
    releases: Mapped[List['Release']] = relationship('Release', backref='service', lazy=True)

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
    status: Mapped[str] = mapped_column(String(20), default='draft')
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(UTC))
    
    service_id: Mapped[int] = mapped_column(ForeignKey('services.id'))

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'version': self.version,
            'changelog': self.changelog,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'service_id': self.service_id
        }