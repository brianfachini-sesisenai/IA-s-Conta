# pages/1_Chat.py

import streamlit as st
import logic
import navigation

st.set_page_config(
    page_title="IA's Conta - Chat Financeiro",
    page_icon="💬",
    layout="centered"
)

# Renderiza a barra lateral personalizada
navigation.make_sidebar()

st.title("💬 Chat Financeiro")

# --- VERIFICAÇÃO DE SEGURANÇA ---
# Se o usuário pulou o formulário, o perfil não existirá.
# Mandamos ele de volta para a página principal.
if 'user_profile' not in st.session_state:
    st.warning("Ops! Parece que você ainda não preencheu seu perfil.")
    st.info("Por favor, preencha o questionário na página inicial para começar.")
    st.page_link("main.py", label="Voltar para o Início", icon="🏠")
    st.stop()

# --- INICIALIZAÇÃO DO CLIENTE DA API ---
client = logic.initialize_client()
if not client:
    st.error("Não foi possível conectar à IA. Verifique as configurações.", icon="🔥")
    st.stop()

# --- INTERFACE DE CHAT ---
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
