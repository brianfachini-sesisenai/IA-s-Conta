import streamlit as st
from huggingface_hub import InferenceClient

# --- 1. CONFIGURAÇÃO DA PÁGINA E ESTADO INICIAL ---

# ALTERAÇÃO 1: Atualiza o título que aparece na aba do navegador.
st.set_page_config(page_title="IA's Conta", page_icon="💡", layout="centered")

# Tenta inicializar o cliente da API do Hugging Face.
try:
    client = InferenceClient(
        model="mistralai/Mistral-7B-Instruct-v0.2",
        token=st.secrets["HUGGINGFACE_API_TOKEN"]
    )
except Exception as e:
    st.error("Erro ao conectar com a API do Hugging Face. Verifique sua chave de API nos Secrets.", icon="🔥")
    st.stop()


# --- 2. FUNÇÃO PRINCIPAL DA IA ---

def get_ai_response(historico_conversa):
    """
    Envia o histórico da conversa para a API e retorna a resposta da IA em tempo real (streaming).
    """
    try:
        response_stream = client.chat_completion(
            messages=historico_conversa,
            max_tokens=2048,
            stream=True
        )
        for chunk in response_stream:
            pedaco_texto = chunk.choices[0].delta.content
            if pedaco_texto:
                yield pedaco_texto

    except Exception as e:
        yield f"\n\nDesculpe, ocorreu um erro ao processar sua solicitação: {e}"


# --- 3. INICIALIZAÇÃO DO ESTADO DA SESSÃO ---

if "messages" not in st.session_state:
    st.session_state.messages = []

if "profile_submitted" not in st.session_state:
    st.session_state.profile_submitted = False


# --- 4. LÓGICA DA INTERFACE (UI) ---

# ALTERAÇÃO 2: Atualiza o título principal exibido na página.
st.title("💡 IA's Conta")

# --- SEÇÃO A: QUESTIONÁRIO INICIAL ---

if not st.session_state.profile_submitted:
    st.info("👋 Olá! Para começar, preciso entender um pouco sobre seu perfil financeiro.")

    with st.form("user_profile_form"):
        renda = st.number_input("Qual é a sua renda mensal (R$)?", min_value=0.0, step=100.0)
        objetivo = st.radio(
            "Qual seu principal objetivo financeiro no momento?",
            ("Apenas guardar dinheiro (criar reserva)", "Investir para o futuro")
        )
        perfil_investidor = "Não se aplica"
        if objetivo == "Investir para o futuro":
            perfil_investidor = st.selectbox(
                "Qual seu perfil de investidor?",
                ("Conservador (prefiro segurança)", "Moderado (busco um equilíbrio)", "Arrojado (busco altos retornos)")
            )
        
        submitted = st.form_submit_button("Começar a Análise!")

        if submitted:
            st.session_state.user_profile = {
                "renda": renda,
                "objetivo": objetivo,
                "perfil_investidor": perfil_investidor
            }
            st.session_state.profile_submitted = True

            # ALTERAÇÃO 3: Atualiza o nome da IA no prompt inicial.
            prompt_inicial = f"""
            Você é a IA do "IA's Conta", um assistente financeiro especialista em finanças pessoais.
            Um usuário com o seguinte perfil acaba de se cadastrar:
            - Renda Mensal: R$ {renda:,.2f}
            - Objetivo Principal: {objetivo}
            - Perfil de Investidor: {perfil_investidor}

            Sua primeira tarefa é gerar três estratégias de economia iniciais, personalizadas e práticas para este usuário.
            Apresente-as em formato de lista numerada. Use uma linguagem encorajadora e comece com uma saudação de boas-vindas.
            """

            # ALTERAÇÃO 4: Atualiza o nome da IA na mensagem de sistema que define sua personalidade.
            mensagem_sistema = {
                "role": "system",
                "content": f"""Você é a IA do "IA's Conta", um assistente financeiro pessoal. Você está conversando com um usuário cujo perfil é: Renda Mensal R${renda:,.2f}, Objetivo: {objetivo}, Perfil: {perfil_investidor}. Sua missão é ajudar o usuário a organizar, analisar e otimizar suas finanças. Responda sempre em português do Brasil, de forma didática e amigável. Baseie suas análises nas informações que o usuário fornecer e no perfil inicial dele."""
            }
            st.session_state.messages.append(mensagem_sistema)
            st.session_state.messages.append({"role": "user", "content": prompt_inicial})
            st.rerun()

# --- SEÇÃO B: INTERFACE DE CHAT ---

if st.session_state.profile_submitted:
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            response = st.write_stream(get_ai_response(st.session_state.messages))
        st.session_state.messages.append({"role": "assistant", "content": response})

    if prompt := st.chat_input("Digite seus gastos, dúvidas ou peça uma análise..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = st.write_stream(get_ai_response(st.session_state.messages))
        st.session_state.messages.append({"role": "assistant", "content": response})
