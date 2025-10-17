import streamlit as st
import logic
import navigation  # Importa nosso novo módulo de navegação

# A configuração da página continua aqui
st.set_page_config(
    page_title="IA's Conta - Início",
    page_icon="🏠",
    layout="centered"
)

# CHAMA NOSSA FUNÇÃO PARA CRIAR A BARRA LATERAL PERSONALIZADA
navigation.make_sidebar()

# O resto do código da página continua exatamente o mesmo...
if "step" not in st.session_state:
    st.session_state.step = 1
if "form_data" not in st.session_state:
    st.session_state.form_data = {}

st.title("💡 Bem-vindo ao IA's Conta")
st.markdown("Seu assistente financeiro pessoal. Para começar, preencha o formulário abaixo.")

if "user_profile" in st.session_state:
    st.success("Seu perfil já foi criado! Você pode ir direto para o chat.")
    st.stop()

# --- QUESTIONÁRIO INICIAL ---
if st.session_state.step == 1:
    with st.form("step1_form"):
        st.subheader("Seu Perfil Básico")
        renda = st.number_input("Renda mensal aproximada (R$)?", min_value=0.0, step=100.0, format="%.2f")
        objetivos = st.multiselect("Principais objetivos financeiros?", ["Organizar finanças", "Diminuir gastos", "Começar a investir"])
        submitted_step1 = st.form_submit_button("Próximo")
        if submitted_step1:
            if not objetivos:
                st.error("Por favor, selecione pelo menos um objetivo.")
            else:
                st.session_state.form_data['renda'] = renda
                st.session_state.form_data['objetivos'] = objetivos
                st.session_state.step = 2 if "Começar a investir" in objetivos else "final"
                st.rerun()

if st.session_state.step == 2:
    with st.form("step2_form"):
        st.subheader("Sobre Investimentos")
        conhecimento_investimento = st.radio("Seu nível de conhecimento?", ["Baixo...", "Médio...", "Alto..."])
        perfil_investidor = st.radio("Seu perfil de investidor?", ["Conservador...", "Moderado...", "Arrojado..."])
        submitted_step2 = st.form_submit_button("Gerar meu plano inicial!")
        if submitted_step2:
            st.session_state.form_data['conhecimento_investimento'] = conhecimento_investimento
            st.session_state.form_data['perfil_investidor'] = perfil_investidor
            st.session_state.step = "final"
            st.rerun()

if st.session_state.step == "final":
    st.session_state.user_profile = logic.create_user_profile(st.session_state.form_data)
    st.session_state.messages = logic.create_initial_messages(st.session_state.user_profile)
    st.switch_page("pages/1_Chat.py")
