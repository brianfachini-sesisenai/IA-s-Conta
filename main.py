# main.py

import streamlit as st
import logic

# Configuração da página principal
st.set_page_config(
    page_title="IA's Conta - Início",
    page_icon="💡",
    layout="centered"
)

# Inicialização do estado da sessão (se necessário)
if "step" not in st.session_state:
    st.session_state.step = 1
if "form_data" not in st.session_state:
    st.session_state.form_data = {}

# --- LÓGICA DA INTERFACE (UI) DA PÁGINA PRINCIPAL ---
st.title("💡 Bem-vindo ao IA's Conta")
st.markdown("Seu assistente financeiro pessoal. Para começar, preencha o formulário abaixo.")

# Se o perfil já foi preenchido, mostra uma mensagem e um link para o chat.
if "user_profile" in st.session_state:
    st.success("Seu perfil já foi criado! Você pode ir direto para o chat.")
    st.page_link("pages/1_Chat.py", label="Ir para o Chat", icon="💬")
    st.stop()

# --- QUESTIONÁRIO INICIAL EM PASSOS ---

# PASSO 1: Informações básicas e objetivos
if st.session_state.step == 1:
    with st.form("step1_form"):
        st.subheader("Seu Perfil Básico")
        renda = st.number_input("Qual é a sua renda mensal aproximada (R$)?", min_value=0.0, step=100.0, format="%.2f")
        objetivos = st.multiselect(
            "Quais são seus principais objetivos financeiros?",
            ["Organizar minhas finanças", "Diminuir meus gastos", "Começar a investir"]
        )
        submitted_step1 = st.form_submit_button("Próximo")
        if submitted_step1:
            if not objetivos:
                st.error("Por favor, selecione pelo menos um objetivo para continuar.")
            else:
                st.session_state.form_data['renda'] = renda
                st.session_state.form_data['objetivos'] = objetivos
                st.session_state.step = 2 if "Começar a investir" in objetivos else "final"
                st.rerun()

# PASSO 2: Detalhes sobre investimentos
if st.session_state.step == 2:
    with st.form("step2_form"):
        st.subheader("Sobre Investimentos")
        conhecimento_investimento = st.radio("Qual seu nível de conhecimento?", ["Baixo...", "Médio...", "Alto..."])
        perfil_investidor = st.radio("Qual seu perfil de investidor?", ["Conservador...", "Moderado...", "Arrojado..."])
        submitted_step2 = st.form_submit_button("Gerar meu plano inicial!")
        if submitted_step2:
            st.session_state.form_data['conhecimento_investimento'] = conhecimento_investimento
            st.session_state.form_data['perfil_investidor'] = perfil_investidor
            st.session_state.step = "final"
            st.rerun()

# PASSO FINAL: Processar tudo e redirecionar
if st.session_state.step == "final":
    # Usar a lógica para criar o perfil e as mensagens iniciais
    st.session_state.user_profile = logic.create_user_profile(st.session_state.form_data)
    st.session_state.messages = logic.create_initial_messages(st.session_state.user_profile)
    
    # Redireciona para a página de chat
    st.switch_page("pages/1_Chat.py")
