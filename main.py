import streamlit as st
import requests

# --- CONFIGURAÇÃO DA API ---
# Coloque sua chave de API do Hugging Face aqui.
# Para um projeto real, use o st.secrets para proteger sua chave!
HF_API_KEY = "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" # <--- SUBSTITUA PELA SUA CHAVE REAL

# URL do modelo que sabemos que está funcionando e é de alta qualidade.
API_URL = "https://api-inference.huggingface.co/models/google/gemma-7b-it"

# Cabeçalho da requisição (igual ao do código C#)
headers = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}

# --- FUNÇÃO PARA CHAMAR A API ---
# Esta função envia o prompt para o Hugging Face e retorna a resposta da IA.
def obter_resposta_ia(prompt):
    """
    Envia um prompt para a API do Hugging Face e retorna a resposta do modelo.
    """
    # Corpo da requisição com os parâmetros do modelo
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 1024,  # Aumentei um pouco para respostas mais completas
            "temperature": 0.7,
            "repetition_penalty": 1.2
        }
    }
    
    try:
        # Faz a requisição POST
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        
        # Verifica se a requisição falhou e retorna uma mensagem de erro clara
        if response.status_code != 200:
            # Erro 503 é comum quando o modelo está carregando
            if response.status_code == 503:
                return "O modelo de IA está carregando. Por favor, aguarde 20 segundos e tente novamente."
            return f"Erro ao contatar a API: {response.status_code} - {response.text}"
            
        # Extrai o texto gerado da resposta JSON
        result = response.json()
        generated_text = result[0].get('generated_text', "Não foi possível obter uma resposta.")
        
        # Limpa a resposta, removendo o prompt que o modelo às vezes repete
        if generated_text.startswith(prompt):
            return generated_text[len(prompt):].strip()
            
        return generated_text

    except requests.exceptions.RequestException as e:
        return f"Erro de conexão: {e}"

# --- INTERFACE DO CHAT COM STREAMLIT ---

st.set_page_config(page_title="Assistente Financeiro", page_icon="💰")
st.title("Assistente Financeiro com IA 🤖")
st.caption("Um protótipo para o projeto da UC de Boas Práticas.")

# Inicializa o histórico do chat na "memória" da sessão do Streamlit
# Isso garante que a conversa não seja perdida a cada interação.
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Adiciona uma mensagem de boas-vindas do assistente na primeira vez
    st.session_state.messages.append(
        {"role": "assistant", "content": "Olá! Sou seu assistente financeiro. Como posso te ajudar a organizar suas finanças hoje?"}
    )

# Exibe todas as mensagens do histórico no contêiner do chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Captura a nova mensagem do usuário no campo de input que fica no final da página
if prompt := st.chat_input("Digite sua pergunta sobre finanças..."):
    # 1. Adiciona a mensagem do usuário ao histórico e exibe na tela
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Gera e exibe a resposta do assistente
    with st.chat_message("assistant"):
        # Mostra um indicador de "pensando..." enquanto espera a resposta da API
        with st.spinner("Analisando e gerando sua resposta..."):
            response = obter_resposta_ia(prompt)
            st.markdown(response)
    
    # 3. Adiciona a resposta do assistente ao histórico
    st.session_state.messages.append({"role": "assistant", "content": response})
