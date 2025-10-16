import streamlit as st

def make_sidebar():
    """Cria uma barra lateral personalizada e esconde a navegação padrão."""
    
    # Vamos adicionar nossa nova regra de estilo aqui
    st.markdown(
        """
        <style>
            /* Esconde a navegação padrão do Streamlit baseada em arquivos */
            [data-testid="stSidebarNav"] {display: none;}

            /* --- NOVA REGRA AQUI --- */
            /* Reduz o espaço no topo do conteúdo da barra lateral */
            [data-testid="stSidebar"] > div:first-child {
                padding-top: 1rem; /* O valor padrão é maior. Ajuste se quiser. */
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Cria nossa própria barra lateral
    with st.sidebar:
        st.title("💡 IA's Conta")
        
        st.markdown("<hr style='margin-top: 0px; margin-bottom: 1rem;'>", unsafe_allow_html=True)
        
        st.page_link("main.py", label="Início", icon="🏠")

        # Mostra o link para o Chat apenas se o perfil do usuário já foi criado
        if 'user_profile' in st.session_state:
            st.page_link("pages/1_Chat.py", label="Chat Financeiro", icon="💬")
