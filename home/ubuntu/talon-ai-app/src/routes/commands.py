from flask import Blueprint, request, jsonify
from src.models.command import Command, VoiceSession, db
import json
from datetime import datetime

commands_bp = Blueprint('commands', __name__)

@commands_bp.route('/commands', methods=['GET'])
def get_commands():
    """
    Listar todos os comandos personalizados.
    """
    try:
        commands = Command.query.filter_by(is_active=True).all()
        return jsonify({
            'success': True,
            'commands': [cmd.to_dict() for cmd in commands]
        })
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar comandos: {str(e)}'}), 500

@commands_bp.route('/commands', methods=['POST'])
def create_command():
    """
    Criar um novo comando personalizado.
    """
    try:
        data = request.get_json()
        
        required_fields = ['name', 'trigger_phrase', 'action_type', 'action_data']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo obrigatório: {field}'}), 400
        
        # Verificar se já existe um comando com o mesmo nome
        existing = Command.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({'error': 'Já existe um comando com esse nome'}), 400
        
        # Validar action_data como JSON
        try:
            if isinstance(data['action_data'], str):
                json.loads(data['action_data'])
        except json.JSONDecodeError:
            return jsonify({'error': 'action_data deve ser um JSON válido'}), 400
        
        command = Command(
            name=data['name'],
            trigger_phrase=data['trigger_phrase'],
            action_type=data['action_type'],
            action_data=data['action_data'] if isinstance(data['action_data'], str) else json.dumps(data['action_data']),
            description=data.get('description', ''),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(command)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'command': command.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao criar comando: {str(e)}'}), 500

@commands_bp.route('/commands/<int:command_id>', methods=['PUT'])
def update_command(command_id):
    """
    Atualizar um comando existente.
    """
    try:
        command = Command.query.get_or_404(command_id)
        data = request.get_json()
        
        # Atualizar campos se fornecidos
        if 'name' in data:
            command.name = data['name']
        if 'trigger_phrase' in data:
            command.trigger_phrase = data['trigger_phrase']
        if 'action_type' in data:
            command.action_type = data['action_type']
        if 'action_data' in data:
            command.action_data = data['action_data'] if isinstance(data['action_data'], str) else json.dumps(data['action_data'])
        if 'description' in data:
            command.description = data['description']
        if 'is_active' in data:
            command.is_active = data['is_active']
        
        command.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'command': command.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao atualizar comando: {str(e)}'}), 500

@commands_bp.route('/commands/<int:command_id>', methods=['DELETE'])
def delete_command(command_id):
    """
    Deletar um comando (soft delete).
    """
    try:
        command = Command.query.get_or_404(command_id)
        command.is_active = False
        command.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Comando desativado com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao deletar comando: {str(e)}'}), 500

@commands_bp.route('/sessions', methods=['POST'])
def log_session():
    """
    Registrar uma sessão de uso do controle por voz.
    """
    try:
        data = request.get_json()
        
        session = VoiceSession(
            session_id=data.get('session_id', ''),
            command_text=data.get('command_text', ''),
            intent=data.get('intent'),
            entities=json.dumps(data.get('entities', {})),
            response=data.get('response', ''),
            execution_time=data.get('execution_time', 0.0),
            success=data.get('success', True),
            error_message=data.get('error_message')
        )
        
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'session': session.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao registrar sessão: {str(e)}'}), 500

@commands_bp.route('/sessions', methods=['GET'])
def get_sessions():
    """
    Listar sessões de uso (últimas 100).
    """
    try:
        sessions = VoiceSession.query.order_by(VoiceSession.created_at.desc()).limit(100).all()
        return jsonify({
            'success': True,
            'sessions': [session.to_dict() for session in sessions]
        })
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar sessões: {str(e)}'}), 500

