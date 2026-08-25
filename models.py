from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Service(db.Model):
    __tablename__ = 'services'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    repository_url = db.Column(db.String(200))
    releases = db.relationship('Release', backref='service', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'repository_url': self.repository_url
        }

class Release(db.Model):
    __tablename__ = 'releases'
    
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(50), nullable=False)
    changelog = db.Column(db.Text)
    status = db.Column(db.String(20), default='draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'version': self.version,
            'changelog': self.changelog,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'service_id': self.service_id
        }