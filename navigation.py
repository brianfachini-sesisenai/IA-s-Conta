import streamlit as st
import logic

def ensure_session_state():
    """
    Esta é a função mais importante. Ela roda em cada página e garante
    que, se o usuário estiver logado, o estado da aplicação (cliente da IA, etc.)
    esteja sempre inicializado e consistente.
    """
    # Se o usuário está logado, verificamos se o cliente da IA existe.
    if st.session_state.get("authenticated"):
        # Se o cliente da IA não existe na sessão ou falhou na criação anterior,
        # tentamos inicializá-lo novamente.
        if "api_client" not in st.session_state or st.session_state.api_client is None:
            st.session_state.api_client = logic.initialize_client()

def make_sidebar():
    """Cria uma barra lateral personalizada com o botão de logout no final."""
    
    st.markdown(
        """
        <style>
            /* Esconde a navegação padrão do Streamlit */
            [data-testid="stSidebarNav"] {display: none;}

            /* Estilos de espaçamento que já tinhamos */
            [data-testid="stSidebarHeader"] {padding-top: 0.5rem !important; margin-bottom: 0rem !important;}
            [data-testid="stSidebarContent"] h1 {padding-top: 0rem !important; padding-bottom: 0.25rem !important;}

            /* --- NOVO ESTILO PARA A SEÇÃO DE LOGOUT --- */
            /* Cria um container fixo no final da sidebar */
            .logout-section {
                position: absolute;
                bottom: 1rem; /* Espaçamento da base */
                width: 90%;   /* Largura relativa à sidebar */
                padding-left: 1rem;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # --- NAVEGAÇÃO PRINCIPAL ---
    with st.sidebar:
        st.title(f"💡 IA's Conta")
        st.write(f"Bem-vindo, **{st.session_state.username}**!")
        st.markdown("<hr style='margin-top: 0px; margin-bottom: 1rem;'>", unsafe_allow_html=True)
        
        st.page_link("main.py", label="Início", icon="🏠")
        
        # O link para o chat só aparece se o perfil estiver completo.
        # Usamos .get() para evitar erros se a chave ainda não existir.
        if st.session_state.get("profile_complete", False):
            st.page_link("pages/1_Chat.py", label="Chat Financeiro", icon="💬")
        
        if st.session_state.get("username") == "admin":
            st.divider()
            st.page_link("pages/2_Admin.py", label="Gerenciar Usuários", icon="👨‍💼")
            
    # --- LÓGICA DO BOTÃO DE LOGOUT NO FINAL DA SIDEBAR ---
    # Usamos st.markdown para criar um 'div' com uma classe CSS customizada
    st.sidebar.markdown('<div class="logout-section">', unsafe_allow_html=True)
    st.sidebar.divider() # Uma linha para separar visualmente
    
    # O botão de logout agora é criado dentro deste 'div'
    if st.sidebar.button("Sair da Conta", use_container_width=True):
        # Limpa todo o estado da sessão para fazer logout
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
