# navigation.py

import streamlit as st

def make_sidebar():
    """Cria uma barra lateral personalizada com o botão de logout fixo no fundo."""
    
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {display: none;}
            [data-testid="stSidebarHeader"] {padding-top: 0.5rem !important;}
            [data-testid="stSidebarContent"] h1 {padding-top: 0rem !important; padding-bottom: 0.25rem !important;}
            
            [data-testid="stSidebarContent"] {
                display: flex;
                flex-direction: column;
                min-height: 90vh;
            }
            .logout-section {
                margin-top: auto;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    with st.sidebar:
        st.title(f"💡 IA's Conta")
        st.write(f"Bem-vindo, **{st.session_state.username}**!")
        st.markdown("<hr style='margin-top: 0px; margin-bottom: 1rem;'>", unsafe_allow_html=True)
        
        st.page_link("main.py", label="Início", icon="🏠")
        if st.session_state.get("profile_complete", False):
            st.page_link("pages/1_Chat.py", label="Chat Financeiro", icon="💬")
        
        if st.session_state.get("username") == "admin":
            st.divider()
            st.page_link("pages/2_Admin.py", label="Gerenciar Usuários", icon="👨‍💼")

        st.markdown('<div class="logout-section">', unsafe_allow_html=True)
        st.divider()
        if st.button("Sair da Conta", use_container_width=True):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
