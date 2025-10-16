# main.py
import streamlit as st
import auth
import logic
import navigation

# Configuração da página principal
st.set_page_config(page_title="IA's Conta", page_icon="💡")

# --- INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "view" not in st.session_state:
    st.session_state.view = "login"
if "step" not in st.session_state:
    st.session_state.step = 1

# --- FUNÇÕES DE TELA (LOGIN E CADASTRO) ---
def tela_login():
    st.header("🔐 Login")
    with st.form("login_form"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        if st.form_submit_button("Entrar", type="primary"):
            if auth.verificar_login(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")
    if st.button("Ainda não tem conta? Cadastre-se"):
        st.session_state.view = "cadastro"
        st.rerun()

def tela_cadastro():
    st.header("📝 Cadastro de Usuário")
    with st.form("cadastro_form"):
        novo_usuario = st.text_input("Escolha um nome de usuário")
        nova_senha = st.text_input("Escolha uma senha", type="password")
        if st.form_submit_button("Cadastrar", type="primary"):
            resultado = auth.registrar_novo_usuario(novo_usuario, nova_senha)
            if resultado.startswith("Sucesso"):
                st.success(resultado + " Agora você pode fazer o login.")
                st.session_state.view = "login"
                st.rerun()
            else:
                st.error(resultado)
    if st.button("🔙 Voltar ao Login"):
        st.session_state.view = "login"
        st.rerun()

# --- CONTROLE PRINCIPAL DE VISUALIZAÇÃO ---

# Se o usuário NÃO está logado, mostra as telas de login/cadastro
if not st.session_state.authenticated:
    st.title("💡 Bem-vindo ao IA's Conta")
    if st.session_state.view == "login":
        tela_login()
    else:
        tela_cadastro()
else:
    # Se o usuário ESTÁ logado, mostra a barra lateral
    navigation.make_sidebar()

    # E agora, verifica se o perfil financeiro foi preenchido
    if "user_profile" in st.session_state:
        # Se sim, boas-vindas e link para o chat
        st.title(f"Olá, {st.session_state.username}!")
        st.success("Seu perfil financeiro está pronto. Você pode ir direto para o chat e começar a interagir com seu assistente.")
        st.page_link("pages/1_Chat.py", label="Ir para o Chat", icon="💬")
    else:
        # Se não, mostra o questionário para criar o perfil
        st.title("Vamos criar seu perfil financeiro")
        # (Aqui entra a lógica do seu questionário, que já tínhamos)
        if st.session_state.step == 1:
            with st.form("step1_form"):
                st.subheader("Seu Perfil Básico")
                renda = st.number_input("Renda mensal (R$)?", min_value=0.0, step=100.0, format="%.2f")
                objetivos = st.multiselect("Objetivos financeiros?", ["Organizar finanças", "Diminuir gastos", "Começar a investir"])
                if st.form_submit_button("Próximo"):
                    if not objetivos: st.error("Selecione pelo menos um objetivo.")
                    else:
                        st.session_state.form_data = {'renda': renda, 'objetivos': objetivos}
                        st.session_state.step = 2 if "Começar a investir" in objetivos else "final"
                        st.rerun()
        
        if st.session_state.step == 2:
            with st.form("step2_form"):
                st.subheader("Sobre Investimentos")
                conhecimento = st.radio("Nível de conhecimento?", ["Baixo...", "Médio...", "Alto..."])
                perfil = st.radio("Perfil de investidor?", ["Conservador...", "Moderado...", "Arrojado..."])
                if st.form_submit_button("Gerar meu plano inicial!"):
                    st.session_state.form_data['conhecimento_investimento'] = conhecimento
                    st.session_state.form_data['perfil_investidor'] = perfil
                    st.session_state.step = "final"
                    st.rerun()

        if st.session_state.step == "final":
            st.session_state.user_profile = logic.create_user_profile(st.session_state.form_data)
            st.session_state.messages = logic.create_initial_messages(st.session_state.user_profile)
            st.switch_page("pages/1_Chat.py")
