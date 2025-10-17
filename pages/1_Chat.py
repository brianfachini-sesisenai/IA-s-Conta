import streamlit as st
import logic
import navigation

# --- CONFIGURAÇÃO E ESTILO UNIVERSAL ---
st.set_page_config(page_title="IA's Conta - Chat", page_icon="💬")
st.markdown("<style>[data-testid='stSidebarNav'] {display: none;}</style>", unsafe_allow_html=True)

# --- GARANTE O ESTADO DA SESSÃO ---
navigation.ensure_session_state()

# --- VERIFICAÇÕES DE SEGURANÇA ---
if not st.session_state.get("authenticated"):
    st.error("Acesso negado. Por favor, faça o login."); st.page_link("main.py", label="Ir para o Login"); st.stop()

if not st.session_state.get("profile_complete", False):
    st.warning("Ops! Seu perfil financeiro não foi preenchido."); st.info("Por favor, complete o questionário na página inicial."); st.page_link("main.py", label="Completar Perfil"); st.stop()

client = st.session_state.get("api_client")
if not client:
    st.error("A conexão com a IA falhou. Por favor, faça o login novamente."); st.page_link("main.py", label="Voltar para o Login"); st.stop()

# Se tudo estiver OK, mostre a interface.
navigation.make_sidebar()
st.title("💬 Chat Financeiro")

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
