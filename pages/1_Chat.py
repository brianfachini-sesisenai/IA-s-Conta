import streamlit as st
import logic
import navigation  # Importa nosso novo módulo de navegação

# A configuração da página continua aqui
st.set_page_config(
    page_title="IA's Conta - Chat Financeiro",
    page_icon="💬",
    layout="centered"
)

# CHAMA NOSSA FUNÇÃO PARA CRIAR A BARRA LATERAL PERSONALIZADA
navigation.make_sidebar()

# O resto do código da página continua exatamente o mesmo...
st.title("💬 Chat Financeiro")

if 'user_profile' not in st.session_state:
    st.warning("Ops! Parece que você ainda não preencheu seu perfil.")
    st.info("Por favor, preencha o questionário na página inicial para começar.")
    st.page_link("main.py", label="Voltar para o Início", icon="🏠")
    st.stop()

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
