# pages/1_Chat.py
import streamlit as st
import logic
import navigation

# --- CONFIGURAÇÃO E ESTILO UNIVERSAL ---
st.set_page_config(page_title="IA's Conta - Chat", page_icon="💬")
st.markdown("<style>[data-testid='stSidebarNav'] {display: none;}</style>", unsafe_allow_html=True)

# --- VERIFICAÇÕES DE SEGURANÇA ---
# 1. O usuário está logado?
if not st.session_state.get("authenticated"):
    st.error("Acesso negado. Por favor, faça o login na página inicial.")
    st.page_link("main.py", label="Ir para o Login", icon="🏠")
    st.stop()

# 2. O perfil financeiro foi criado?
if 'user_profile' not in st.session_state:
    st.warning("Ops! Parece que você ainda não preencheu seu perfil financeiro.")
    st.info("Por favor, preencha o questionário na página inicial para começar.")
    st.page_link("main.py", label="Voltar para o Início", icon="🏠")
    st.stop()

# 3. A conexão com a IA foi estabelecida com sucesso?
if 'api_client' not in st.session_state or not st.session_state.api_client:
    st.error("Não foi possível conectar à IA. Verifique as configurações e tente fazer o login novamente.")
    st.page_link("main.py", label="Voltar para o Login", icon="🏠")
    st.stop()

# Se todas as verificações passaram, mostre a interface.
navigation.make_sidebar()
st.title("💬 Chat Financeiro")

# Pega o cliente da IA que foi guardado na sessão
client = st.session_state.api_client

# --- INTERFACE DE CHAT (código que já tínhamos) ---
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        response = st.write_stream(logic.get_ai_response(client, st.session_state.messages))
    st.session_state.messages.append({"role": "assistant", "content": response})

if prompt := st.chat_input("Digite seus gastos, dúvidas ou peça uma análise..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        response = st.write_stream(logic.get_ai_response(client, st.session_state.messages))
    st.session_state.messages.append({"role": "assistant", "content": response})
