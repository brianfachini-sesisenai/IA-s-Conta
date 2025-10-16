import streamlit as st

def make_sidebar():
    """Cria uma barra lateral personalizada para usuários logados."""
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {display: none;}
            [data-testid="stSidebarHeader"] {padding-top: 0.5rem !important; margin-bottom: 0rem !important;}
            [data-testid="stSidebarContent"] h1 {padding-top: 0rem !important; padding-bottom: 0.25rem !important;}
        </style>
        """,
        unsafe_allow_html=True
    )

    with st.sidebar:
        st.title(f"💡 IA's Conta")
        st.write(f"Bem-vindo, **{st.session_state.username}**!")
        st.markdown("<hr style='margin-top: 0px; margin-bottom: 1rem;'>", unsafe_allow_html=True)
        
        st.page_link("main.py", label="Início", icon="🏠")
        if 'user_profile' in st.session_state:
            st.page_link("pages/1_Chat.py", label="Chat Financeiro", icon="💬")
        
        # Link condicional para a página de Admin
        if st.session_state.get("username") == "admin":
            st.divider()
            st.page_link("pages/2_Admin.py", label="Gerenciar Usuários", icon="👨‍💼")

        st.divider()
        if st.button("Sair da Conta"):
            # Limpa todo o estado da sessão para fazer logout
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()
