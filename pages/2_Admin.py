# pages/2_Admin.py

import streamlit as st
import auth
import pandas as pd
import navigation

# --- CONFIGURAÇÃO E ESTILO UNIVERSAL ---
st.set_page_config(page_title="IA's Conta - Admin", page_icon="👨‍💼")
st.markdown("<style>[data-testid='stSidebarNav'] {display: none;}</style>", unsafe_allow_html=True)

# --- VERIFICAÇÃO DE SEGURANÇA ---
# Garante que apenas o admin logado possa ver esta página
if not st.session_state.get("authenticated") or st.session_state.get("username") != "admin":
    st.error("Acesso restrito à administração.")
    st.page_link("main.py", label="Voltar para o Início", icon="🏠")
    st.stop()

# Renderiza a barra lateral personalizada
navigation.make_sidebar()

# --- INTERFACE DE GERENCIAMENTO DE USUÁRIOS ---
st.title("👨‍💼 Painel de Gerenciamento de Usuários")

with st.expander("➕ Criar Novo Usuário", expanded=True):
    with st.form("create_user_form"):
        new_username = st.text_input("Nome do novo usuário")
        new_password = st.text_input("Senha do novo usuário", type="password")
        submitted = st.form_submit_button("Criar Usuário")
        if submitted:
            resultado = auth.registrar_novo_usuario(new_username, new_password)
            if resultado.startswith("Sucesso"):
                st.success(resultado)
                st.rerun()
            else:
                st.error(resultado)

st.divider()

st.write("**Modificar ou Excluir Usuários Existentes**")
try:
    conn = auth.get_db_connection()
    todos_usuarios = conn.query("SELECT username, criado_em FROM usuarios WHERE username != 'admin' ORDER BY criado_em DESC;", ttl=0)
    
    if todos_usuarios.empty:
        st.warning("Nenhum usuário cadastrado (além do admin).")
    else:
        # Usamos uma cópia para edição para evitar problemas de estado
        usuarios_para_editar = todos_usuarios.copy()
        usuarios_para_editar["nova_senha"] = ""
        usuarios_para_editar["deletar"] = False

        edited_df = st.data_editor(
            usuarios_para_editar,
            column_config={
                "username": st.column_config.TextColumn("Usuário (pode ser editado)"),
                "criado_em": st.column_config.DatetimeColumn("Data de Criação", disabled=True),
                "nova_senha": st.column_config.TextColumn("Definir Nova Senha"),
                "deletar": st.column_config.CheckboxColumn("Deletar?")
            },
            hide_index=True, use_container_width=True, key="admin_data_editor"
        )
        
        if st.button("Salvar Alterações", type="primary"):
            for i, original_row in todos_usuarios.iterrows():
                edited_row = edited_df.iloc[i]
                original_username = original_row["username"]
                
                if edited_row["deletar"]:
                    auth.delete_user(original_username)
                    st.toast(f"Usuário '{original_username}' deletado.")
                    continue

                if original_username != edited_row["username"]:
                    success, message = auth.update_username(original_username, edited_row["username"])
                    if success:
                        st.toast(message)
                        original_username = edited_row["username"]
                    else:
                        st.error(message)

                if edited_row["nova_senha"]:
                    auth.update_user_password(original_username, edited_row["nova_senha"])
                    st.toast(f"Senha de '{original_username}' atualizada.")
            
            st.success("Alterações processadas! Recarregando a lista...")
            st.rerun()
except Exception as e:
    st.error(f"Não foi possível carregar os usuários: {e}")
