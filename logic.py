# logic.py

import streamlit as st
from huggingface_hub import InferenceClient

def initialize_client():
    """Inicializa e retorna o cliente da API do Hugging Face."""
    try:
        client = InferenceClient(
            model="mistralai/Mistral-7B-Instruct-v0.2",
            token=st.secrets["HUGGINGFACE_API_TOKEN"]
        )
        return client
    except Exception:
        return None

def get_ai_response(client, historico_conversa):
    """Envia o histórico para a API e retorna a resposta da IA."""
    if not client:
        yield "Erro: O cliente da API não foi inicializado corretamente."
        return
    try:
        response_stream = client.chat_completion(
            messages=historico_conversa, max_tokens=2048, stream=True
        )
        for chunk in response_stream:
            pedaco_texto = chunk.choices[0].delta.content
            if pedaco_texto and "</s>" not in pedaco_texto:
                yield pedaco_texto
    except Exception as e:
        yield f"\n\nDesculpe, ocorreu um erro: {e}"

def create_user_profile(form_data):
    """Processa os dados do formulário e cria um dicionário de perfil do usuário."""
    perfil_limpo = form_data.get('perfil_investidor', 'Não se aplica').split(':')[0]
    conhecimento_limpo = form_data.get('conhecimento_investimento', 'Não se aplica').split(' ')[0]

    return {
        "renda": form_data['renda'],
        "objetivos": ", ".join(form_data['objetivos']),
        "perfil_investidor": perfil_limpo,
        "conhecimento_investimento": conhecimento_limpo
    }

def create_initial_messages(user_profile):
    """Cria a mensagem de sistema e o prompt inicial para começar o chat."""
    prompt_inicial = f"""
    Você é a IA do "IA's Conta", um assistente financeiro especialista.
    Um usuário com o seguinte perfil detalhado acaba de se cadastrar:
    - Renda Mensal: R$ {user_profile['renda']:,.2f}
    - Objetivos: {user_profile['objetivos']}
    - Nível de conhecimento sobre investimentos: {user_profile['conhecimento_investimento']}
    - Perfil de Investidor: {user_profile['perfil_investidor']}
    Sua primeira tarefa é gerar três estratégias iniciais, práticas e personalizadas para este usuário.
    """
    mensagem_sistema = {
        "role": "system",
        "content": f"""Você é a IA do "IA's Conta", um assistente financeiro pessoal, didático e confiável. Você está conversando com um usuário com este perfil: {user_profile}.
        REGRAS:
        1. Responda TUDO em português do Brasil.
        2. Adapte sua linguagem ao nível de conhecimento do usuário ('{user_profile['conhecimento_investimento']}').
        3. Sempre inclua um aviso de que suas sugestões não são recomendações de investimento formais.
        """
    }
    return [mensagem_sistema, {"role": "user", "content": prompt_inicial}]
