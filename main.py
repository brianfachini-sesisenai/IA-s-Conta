# main.py

import streamlit as st
import auth
import logic
import navigation

# --- CONFIGURAÇÃO UNIVERSAL E ESTILOS ---
# Esta configuração é a primeira coisa a ser lida
st.set_page_config(page_title="IA's Conta", page_icon="💡")

# Esconde a navegação padrão do Streamlit IMEDIATAMENTE.
# Isso garante que a "sidebar feia" nunca apareça.
st.markdown(
    "<style>[data-testid='stSidebarNav'] {display: none;}</style>", 
    unsafe_allow_html=True
)

# --- INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
# Define os estados iniciais se eles não existirem.
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "view" not in st.session_state:
    st.session_state.view = "login"

# --- FUNÇÃO CENTRAL DE INICIALIZAÇÃO PÓS-LOGIN ---
def initialize_app_session():
    """
    Função para rodar UMA VEZ após o login.
    Inicializa a conexão com a IA e verifica o estado do perfil do usuário.
    """
    # 1. Se o cliente da IA ainda não foi inicializado, faz isso agora.
    if 'api_client' not in st.session_state:
        st.session_state.api_client = logic.initialize_client()

    # 2. Define o estado do perfil. No futuro, isso viria de uma consulta ao banco.
    #    Por agora, se a flag 'profile_complete' não existe, ela é False.
    if 'profile_complete' not in st.session_state:
        st.session_state.profile_complete = False

# --- TELAS DE LOGIN E CADASTRO ---
def tela_login():
    st.header("🔐 Login")
    with st.form("login_form"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        if st.form_submit_button("Entrar", type="primary"):
            if auth.verificar_login(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                initialize_app_session() # Roda a inicialização ANTES de recarregar
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")
    if st.button("Ainda não tem conta? Cadastre-se"):
        st.session_state.view = "cadastro"; st.rerun()

def tela_cadastro():
    st.header("📝 Cadastro de Usuário")
    with st.form("cadastro_form"):
        novo_usuario = st.text_input("Escolha um nome de usuário")
        nova_senha = st.text_input("Escolha uma senha", type="password")
        if st.form_submit_button("Cadastrar", type="primary"):
            resultado = auth.registrar_novo_usuario(novo_usuario, nova_senha)
            if resultado.startswith("Sucesso"):
                st.success(resultado + " Agora você pode fazer o login.")
                st.session_state.view = "login"; st.rerun()
            else:
                st.error(resultado)
    if st.button("🔙 Voltar ao Login"):
        st.session_state.view = "login"; st.rerun()

# --- CONTROLE PRINCIPAL DE VISUALIZAÇÃO ---
if not st.session_state.authenticated:
    st.title("💡 Bem-vindo ao IA's Conta")
    if st.session_state.view == "login":
        tela_login()
    else:
        tela_cadastro()
else:
    # Se o usuário ESTÁ logado, a barra lateral personalizada é exibida.
    navigation.make_sidebar()

    # Agora, a verificação é sobre o estado do perfil.
    if not st.session_state.get("profile_complete", False):
        st.title("Vamos criar seu perfil financeiro")
        if 'step' not in st.session_state: st.session_state.step = 1
        
        if st.session_state.step == 1:
            with st.form("step1_form"):
                st.subheader("Seu Perfil Básico")
                renda = st.number_input("Renda mensal (R$)?", min_value=0.0)
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
                if st.form_submit_button("Gerar plano!"):
                    st.session_state.form_data['conhecimento_investimento'] = conhecimento
                    st.session_state.form_data['perfil_investidor'] = perfil
                    st.session_state.step = "final"
                    st.rerun()

        if st.session_state.step == "final":
            st.session_state.user_profile = logic.create_user_profile(st.session_state.form_data)
            st.session_state.messages = logic.create_initial_messages(st.session_state.user_profile)
            st.session_state.profile_complete = True # Marca que o perfil foi criado
            del st.session_state.step # Limpa o estado do formulário
            del st.session_state.form_data # Limpa os dados do formulário
            st.switch_page("pages/1_Chat.py")
    else:
        # Se o perfil já existe, boas-vindas e link para o chat.
        st.title(f"Olá novamente, {st.session_state.username}!")
        st.success("Seu perfil financeiro está pronto. Vá para o chat para interagir com seu assistente.")
        st.page_link("pages/1_Chat.py", label="Ir para o Chat", icon="💬")
