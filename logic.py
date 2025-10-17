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
    except Exception as e:
        st.error(f"Erro ao inicializar o cliente da API: {e}", icon="🔥")
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
        yield f"\n\nDesculpe, ocorreu um erro ao processar sua solicitação: {e}"

def create_user_profile(form_data):
    """Processa os dados do formulário e cria um dicionário limpo de perfil do usuário."""
    perfil_limpo = form_data.get('perfil_investidor', 'Não se aplica').split(':')[0]
    conhecimento_limpo = form_data.get('conhecimento_investimento', 'Não se aplica').split(' ')[0]

    user_profile = {
        "renda": form_data['renda'],
        "objetivos": ", ".join(form_data['objetivos']),
        "perfil_investidor": perfil_limpo,
        "conhecimento_investimento": conhecimento_limpo
    }
    return user_profile

def create_initial_messages(user_profile):
    """Cria a mensagem de sistema e o prompt inicial para começar o chat."""
    prompt_inicial = f"""
    Sua primeira tarefa é gerar três estratégias iniciais, práticas e altamente personalizadas para um usuário com este perfil:
    - Renda Mensal: R$ {user_profile['renda']:,.2f}
    - Objetivos: {user_profile['objetivos']}
    - Nível de conhecimento sobre investimentos: {user_profile['conhecimento_investimento']}
    - Perfil de Investidor: {user_profile['perfil_investidor']}
    Apresente-as em lista numerada. Use uma linguagem encorajadora e comece com uma saudação de boas-vindas.
    """

    mensagem_sistema = {
        "role": "system",
        "content": f"""Você é a IA do "IA's Conta", um assistente financeiro pessoal. Sua personalidade é didática, paciente e confiável. Você está conversando com um usuário com este perfil: {user_profile}.
        REGRAS PRINCIPAIS:
        1.  **IDIOMA:** Responda TUDO exclusivamente em português do Brasil.
        2.  **ADAPTAÇÃO:** Adapte sua linguagem ao nível de conhecimento do usuário ('{user_profile['conhecimento_investimento']}'). Se for 'Baixo', seja extremamente simples. Se 'Médio', explique conceitos. Se 'Alto', seja técnico.
        3.  **SEGURANÇA:** Sempre inclua um aviso de que suas sugestões não são recomendações de investimento formais.
        """
    }
    
    return [mensagem_sistema, {"role": "user", "content": prompt_inicial}]
