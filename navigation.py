import streamlit as st

def make_sidebar():
    """Cria uma barra lateral personalizada com o botão de logout fixo no fundo."""
    
    st.markdown(
        """
        <style>
            /* Esconde a navegação padrão do Streamlit */
            [data-testid="stSidebarNav"] {display: none;}

            /* Estilos de espaçamento que já tínhamos */
            [data-testid="stSidebarHeader"] {padding-top: 0.5rem !important;}
            [data-testid="stSidebarContent"] h1 {padding-top: 0rem !important; padding-bottom: 0.25rem !important;}

            /* --- NOVA ABORDAGEM COM FLEXBOX (A SOLUÇÃO DEFINITIVA) --- */
            
            /* 1. Transforma o container principal da sidebar em um layout flexível vertical */
            [data-testid="stSidebarContent"] {
                display: flex;
                flex-direction: column;
                justify-content: space-between; /* Distribui o espaço */
                height: 95vh; /* Ocupa quase toda a altura da tela */
            }

            /* 2. Cria um container para o conteúdo principal */
            .main-nav {
                /* Este container não precisa de estilos específicos, 
                   o flexbox já vai colocá-lo no topo. */
            }

            /* 3. Cria um container para a seção de logout */
            .logout-section {
                /* Este container será empurrado para o fundo pelo justify-content */
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    with st.sidebar:
        # Envolvemos a navegação principal em um 'div'
        st.markdown('<div class="main-nav">', unsafe_allow_html=True)
        st.title(f"💡 IA's Conta")
        st.write(f"Bem-vindo, **{st.session_state.username}**!")
        st.markdown("<hr style='margin-top: 0px; margin-bottom: 1rem;'>", unsafe_allow_html=True)
        
        st.page_link("main.py", label="Início", icon="🏠")
        if 'user_profile' in st.session_state:
            st.page_link("pages/1_Chat.py", label="Chat Financeiro", icon="💬")
        
        if st.session_state.get("username") == "admin":
            st.divider()
            st.page_link("pages/2_Admin.py", label="Gerenciar Usuários", icon="👨‍💼")
        st.markdown('</div>', unsafe_allow_html=True)


        # Envolvemos a seção de logout em outro 'div'
        st.markdown('<div class="logout-section">', unsafe_allow_html=True)
        st.divider()
        if st.button("Sair da Conta", use_container_width=True):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
