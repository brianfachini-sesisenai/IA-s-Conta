# pages/1_Chat.py
import streamlit as st
import logic
import navigation

st.set_page_config(page_title="IA's Conta - Chat", page_icon="💬")

# --- VERIFICAÇÃO DE SEGURANÇA ---
if not st.session_state.get("authenticated"):
    st.error("Acesso negado. Por favor, faça o login na página inicial.")
    st.page_link("main.py", label="Ir para o Login", icon="🏠")
    st.stop()

navigation.make_sidebar()
st.title("💬 Chat Financeiro")

if 'user_profile' not in st.session_state:
    st.warning("Parece que seu perfil financeiro não foi criado.")
    st.info("Por favor, volte à página inicial para preencher o questionário.")
    st.page_link("main.py", label="Voltar para o Início", icon="🏠")
    st.stop()
client = logic.initialize_client()

client = logic.initialize_client()
if not client:
    st.error("Não foi possível conectar à IA. Verifique as configurações.", icon="🔥")
    st.stop()

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
