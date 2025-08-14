from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Command(db.Model):
    """
    Modelo para armazenar comandos personalizados do usuário.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    trigger_phrase = db.Column(db.String(200), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)  # 'text', 'url', 'script', 'api'
    action_data = db.Column(db.Text, nullable=False)  # JSON string com dados da ação
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'trigger_phrase': self.trigger_phrase,
            'action_type': self.action_type,
            'action_data': self.action_data,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class VoiceSession(db.Model):
    """
    Modelo para armazenar sessões de uso do controle por voz.
    """
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)
    command_text = db.Column(db.Text, nullable=False)
    intent = db.Column(db.String(100))
    entities = db.Column(db.Text)  # JSON string
    response = db.Column(db.Text)
    execution_time = db.Column(db.Float)  # tempo em segundos
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'command_text': self.command_text,
            'intent': self.intent,
            'entities': self.entities,
            'response': self.response,
            'execution_time': self.execution_time,
            'success': self.success,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

