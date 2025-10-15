import streamlit as st
import requests

# --- CONFIGURAÇÃO DA API ---
# [BOA PRÁTICA!] Lendo a chave de API de forma segura a partir dos "Secrets" do Streamlit.
# O nome "HF_API_KEY" deve ser o mesmo que você usou no arquivo de Secrets.
HF_API_KEY = st.secrets["HF_API_KEY"]

# URL do modelo que sabemos que está funcionando e é de alta qualidade.
API_URL = "https://api-inference.huggingface.co/models/google/gemma-7b-it"

# Cabeçalho da requisição (igual ao do código C#)
headers = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}

# --- FUNÇÃO PARA CHAMAR A API ---
# (O resto da função permanece exatamente o mesmo)
def obter_resposta_ia(prompt):
    """
    Envia um prompt para a API do Hugging Face e retorna a resposta do modelo.
    """
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 1024,
            "temperature": 0.7,
            "repetition_penalty": 1.2
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            if response.status_code == 503:
                return "O modelo de IA está carregando. Por favor, aguarde 20 segundos e tente novamente."
            return f"Erro ao contatar a API: {response.status_code} - {response.text}"
            
        result = response.json()
        generated_text = result[0].get('generated_text', "Não foi possível obter uma resposta.")
        
        if generated_text.startswith(prompt):
            return generated_text[len(prompt):].strip()
            
        return generated_text

    except requests.exceptions.RequestException as e:
        return f"Erro de conexão: {e}"

# --- INTERFACE DO CHAT COM STREAMLIT ---
# (Nenhuma mudança necessária aqui, o código abaixo permanece o mesmo)

st.set_page_config(page_title="Assistente Financeiro", page_icon="💰")
st.title("Assistente Financeiro com IA 🤖")
st.caption("Um protótipo para o projeto da UC de Boas Práticas.")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append(
        {"role": "assistant", "content": "Olá! Sou seu assistente financeiro. Como posso te ajudar a organizar suas finanças hoje?"}
    )

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Digite sua pergunta sobre finanças..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analisando e gerando sua resposta..."):
            response = obter_resposta_ia(prompt)
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
