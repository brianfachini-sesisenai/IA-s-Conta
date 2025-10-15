import streamlit as st
import requests

# --- CONFIGURAÇÃO DA API ---

# Tenta ler a chave de API dos "Secrets" do Streamlit.
try:
    HF_API_KEY = st.secrets["HF_API_KEY"]
except (KeyError, FileNotFoundError):
    st.error("ERRO: A chave de API 'HF_API_KEY' não foi encontrada nos Secrets do Streamlit.")
    st.stop() # Interrompe a execução do app se a chave não for encontrada.

# [ETAPA DE DIAGNÓSTICO 1] - VERIFICAR SE A CHAVE FOI CARREGADA CORRETAMENTE
# Esta linha irá exibir os primeiros 7 caracteres da sua chave no app.
# Se você vir "Chave carregada...", significa que o st.secrets está funcionando.
# LEMBRE-SE DE REMOVER ESTA LINHA DEPOIS DE CONFIRMAR QUE FUNCIONA!
st.sidebar.write(f"✔️ Chave carregada. Início: {HF_API_KEY[:7]}...")

# [ETAPA DE DIAGNÓSTICO 2] - USAR O MODELO MAIS ESTÁVEL POSSÍVEL
# Trocamos para o 'gpt2', um modelo clássico que garantidamente tem um endpoint público funcional.
API_URL = "https://api-inference.huggingface.co/models/gpt2"
st.sidebar.write(f"✔️ Usando modelo de teste: {API_URL.split('/')[-1]}")

# Cabeçalho da requisição
headers = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}

# --- FUNÇÃO PARA CHAMAR A API ---
def obter_resposta_ia(prompt):
    """
    Envia um prompt para a API do Hugging Face e retorna a resposta do modelo.
    """
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 150, # gpt2 é mais antigo, respostas menores são mais rápidas
            "temperature": 0.8,
            "repetition_penalty": 1.2
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            if response.status_code == 503:
                return "O modelo de IA está carregando. Por favor, aguarde 20 segundos e tente novamente."
            # Exibe o erro completo para facilitar a depuração
            return f"Erro ao contatar a API: {response.status_code} - {response.text}"
            
        result = response.json()
        generated_text = result[0].get('generated_text', "Não foi possível obter uma resposta.")
        
        if generated_text.startswith(prompt):
            return generated_text[len(prompt):].strip()
            
        return generated_text

    except requests.exceptions.RequestException as e:
        return f"Erro de conexão: {e}"

# --- INTERFACE DO CHAT COM STREAMLIT ---
st.set_page_config(page_title="Assistente Financeiro (Modo Teste)", page_icon="🧪")
st.title("Assistente Financeiro com IA 🤖")
st.caption("Executando em modo de diagnóstico para testar a conexão com a API.")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append(
        {"role": "assistant", "content": "Olá! Estou em modo de teste. Por favor, faça uma pergunta simples para verificar a conexão."}
    )

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Digite 'olá' ou uma pergunta simples..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Testando conexão com a API..."):
            response = obter_resposta_ia(prompt)
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
