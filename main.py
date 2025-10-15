import streamlit as st
import requests

# --- CONFIGURAÇÃO DA API ---

# Tenta ler a chave de API dos "Secrets" do Streamlit.
try:
    HF_API_KEY = st.secrets["HF_API_KEY"]
except (KeyError, FileNotFoundError):
    st.error("ERRO: A chave de API 'HF_API_KEY' não foi encontrada nos Secrets do Streamlit.")
    st.info("Por favor, adicione sua chave do Hugging Face aos Secrets da sua aplicação.")
    st.stop() # Interrompe a execução do app se a chave não for encontrada.

# URL específica para o Mistral-7B-Instruct-v0.3.
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"

# Cabeçalho da requisição
headers = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}

# --- FUNÇÃO PARA CHAMAR A API ---
def obter_resposta_ia(prompt_usuario):
    """
    Formata o prompt para o Mistral, envia para a API e retorna a resposta.
    """
    prompt_formatado = f"[INST] {prompt_usuario} [/INST]"

    payload = {
        "inputs": prompt_formatado,
        "parameters": {
            "max_new_tokens": 1024,
            "temperature": 0.7,
            "repetition_penalty": 1.1
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=45)
        
        if response.status_code != 200:
            if response.status_code == 503:
                return "O modelo de IA está carregando. Por favor, aguarde cerca de 30 segundos e tente novamente."
            return f"Erro ao contatar a API: {response.status_code} - {response.text}"
            
        result = response.json()
        generated_text = result[0].get('generated_text', "Não foi possível obter uma resposta.")
        
        if generated_text.startswith(prompt_formatado):
            return generated_text[len(prompt_formatado):].strip()
            
        return generated_text

    except requests.exceptions.RequestException as e:
        return f"Erro de conexão: {e}"

# --- INTERFACE DO CHAT COM STREAMLIT ---
st.set_page_config(page_title="Assistente Financeiro", page_icon="💰")
st.title("Assistente Financeiro com IA 🤖")
st.caption("Usando o modelo Mistral-7B-Instruct-v0.3")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append(
        {"role": "assistant", "content": "Olá! Sou seu assistente financeiro. Como posso te ajudar hoje?"}
    )

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Digite sua pergunta sobre finanças..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analisando e gerando sua resposta com o Mistral..."):
            response = obter_resposta_ia(prompt)
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
