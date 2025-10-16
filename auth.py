# auth.py
import streamlit as st
from datetime import datetime
import pandas as pd
from sqlalchemy.sql import text

# --- FUNÇÕES DE ACESSO AO BANCO DE DADOS ---

def get_db_connection():
    """Retorna uma conexão com o banco de dados (configurado nos secrets)."""
    return st.connection("supabase_db", type="sql")

# --- FUNÇÕES DE LOGIN E CADASTRO ---

def verificar_login(username, password):
    """Verifica as credenciais do usuário."""
    try:
        conn = get_db_connection()
        df = conn.query("SELECT senha FROM usuarios WHERE username = :username;", params={"username": username}, ttl=0)
        if df.empty: return False
        return df.iloc[0]['senha'] == password
    except Exception as e:
        st.error(f"Erro ao verificar login: {e}")
        return False

def registrar_novo_usuario(username, password):
    """Registra um novo usuário."""
    if not username or not password:
        return "Erro: Nome de usuário e senha não podem estar vazios."
    if username.lower() == "admin":
        return "Erro: Nome de usuário 'admin' é reservado."

    conn = get_db_connection()
    try:
        df_existente = conn.query("SELECT * FROM usuarios WHERE username = :username;", params={"username": username}, ttl=0)
        if not df_existente.empty:
            return "Erro: Nome de usuário já existe."

        with conn.session as s:
            s.execute(
                text("INSERT INTO usuarios (username, senha, criado_em) VALUES (:username, :senha, :criado_em);"),
                params={"username": username, "senha": password, "criado_em": datetime.now()}
            )
            s.commit()
        return "Sucesso: Usuário cadastrado com sucesso!"
    except Exception as e:
        return f"Erro inesperado no banco de dados: {e}"

# --- FUNÇÕES DE GERENCIAMENTO DE USUÁRIOS (PARA ADMIN) ---
# (O resto das suas funções, como delete_user, update_user_password, etc., entram aqui)
# Colei o restante para garantir que tudo esteja no lugar certo.

def delete_user(username):
    try:
        conn = get_db_connection()
        with conn.session as s:
            s.execute(text("DELETE FROM usuarios WHERE username = :username;"), params={"username": username})
            s.commit()
        return True
    except Exception as e:
        st.error(f"Erro ao deletar usuário {username}: {e}")
        return False

def update_user_password(username, new_password):
    if not new_password: return False
    try:
        conn = get_db_connection()
        with conn.session as s:
            s.execute(
                text("UPDATE usuarios SET senha = :new_password WHERE username = :username;"),
                params={"new_password": new_password, "username": username}
            )
            s.commit()
        return True
    except Exception as e:
        st.error(f"Erro ao atualizar senha para {username}: {e}")
        return False

def update_username(old_username, new_username):
    if not new_username: return False, "O novo nome de usuário não pode estar vazio."
    if new_username.lower() == 'admin': return False, "Não é possível renomear um usuário para 'admin'."
    
    conn = get_db_connection()
    try:
        df_existente = conn.query("SELECT * FROM usuarios WHERE username = :username;", params={"username": new_username}, ttl=0)
        if not df_existente.empty:
            return False, f"O nome de usuário '{new_username}' já está em uso."
        
        with conn.session as s:
            s.execute(
                text("UPDATE usuarios SET username = :new_username WHERE username = :old_username;"),
                params={"new_username": new_username, "old_username": old_username}
            )
            s.commit()
        return True, f"Usuário '{old_username}' renomeado para '{new_username}'."
    except Exception as e:
        return False, f"Erro ao renomear usuário: {e}"
