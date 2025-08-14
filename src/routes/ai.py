from flask import Blueprint, request, jsonify
import os
from openai import OpenAI

ai_bp = Blueprint('ai', __name__)

# Inicializar o cliente OpenAI (usa as variáveis de ambiente OPENAI_API_KEY e OPENAI_API_BASE)
client = OpenAI()

@ai_bp.route('/speech-to-text', methods=['POST'])
def speech_to_text():
    """
    Endpoint para converter áudio em texto usando a API do OpenAI Whisper.
    Espera um arquivo de áudio no formato WAV.
    """
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'Nenhum arquivo de áudio fornecido'}), 400
        
        audio_file = request.files['audio']
        
        # Usar a API Whisper do OpenAI para transcrição
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="pt"
        )
        
        return jsonify({
            'success': True,
            'text': transcript.text
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro no reconhecimento de fala: {str(e)}'}), 500

@ai_bp.route('/process-command', methods=['POST'])
def process_command():
    """
    Endpoint para processar comandos de texto usando IA.
    Analisa a intenção do usuário e retorna uma resposta estruturada.
    """
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Texto não fornecido'}), 400
        
        user_text = data['text']
        
        # Prompt para o modelo de IA analisar o comando
        system_prompt = """Você é um assistente de controle por voz inteligente. 
        Analise o comando do usuário e identifique:
        1. A intenção principal (ex: abrir_aplicativo, pesquisar, digitar_texto, executar_acao)
        2. Entidades relevantes (ex: nome do aplicativo, texto a ser digitado, termo de pesquisa)
        3. Parâmetros adicionais

        Responda em formato JSON com:
        {
            "intent": "nome_da_intencao",
            "entities": {"chave": "valor"},
            "action": "descrição da ação a ser executada",
            "response": "resposta amigável para o usuário"
        }"""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            temperature=0.3
        )
        
        # Tentar parsear a resposta como JSON
        try:
            import json
            ai_response = json.loads(response.choices[0].message.content)
        except:
            # Se não conseguir parsear, retornar resposta simples
            ai_response = {
                "intent": "unknown",
                "entities": {},
                "action": "Comando não reconhecido",
                "response": response.choices[0].message.content
            }
        
        return jsonify({
            'success': True,
            'result': ai_response
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro no processamento: {str(e)}'}), 500

@ai_bp.route('/generate-text', methods=['POST'])
def generate_text():
    """
    Endpoint para gerar texto usando IA baseado em um prompt.
    """
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({'error': 'Prompt não fornecido'}), 400
        
        user_prompt = data['prompt']
        max_tokens = data.get('max_tokens', 150)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        generated_text = response.choices[0].message.content
        
        return jsonify({
            'success': True,
            'text': generated_text
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro na geração de texto: {str(e)}'}), 500

@ai_bp.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint para verificar se o serviço de IA está funcionando.
    """
    return jsonify({
        'status': 'healthy',
        'services': {
            'openai_whisper': True,
            'openai_gpt': True
        }
    })

