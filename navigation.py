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

            /* --- A SOLUÇÃO CORRETA E FINAL --- */
            
            /* 1. Transforma o container da sidebar em um layout flexível */
            [data-testid="stSidebarContent"] {
                display: flex;
                flex-direction: column;
                min-height: 90vh; /* Garante que o container tenha altura suficiente */
            }

            /* 2. A MÁGICA: Empurra a seção de logout para o fundo */
            .logout-section {
                margin-top: auto; /* Ocupa todo o espaço vertical disponível acima dele */
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    with st.sidebar:
        # --- NAVEGAÇÃO PRINCIPAL (Não precisa mais de um div wrapper) ---
        st.title(f"💡 IA's Conta")
        st.write(f"Bem-vindo, **{st.session_state.username}**!")
        st.markdown("<hr style='margin-top: 0px; margin-bottom: 1rem;'>", unsafe_allow_html=True)
        
        st.page_link("
