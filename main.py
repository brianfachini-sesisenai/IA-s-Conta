import streamlit as st
from huggingface_hub import InferenceClient

# --- 1. CONFIGURAÇÃO DA PÁGINA E ESTADO INICIAL ---

# Configura o título da página, ícone e layout. Deve ser a primeira chamada do Streamlit.
st.set_page_config(page_title="FinAI - Seu Gestor Financeiro", page_icon="💡", layout="centered")

# Tenta inicializar o cliente da API do Hugging Face.
# A chave é lida dos "Secrets" do Streamlit, que é o local seguro para armazená-la.
try:
    client = InferenceClient(
        model="mistralai/Mistral-7B-Instruct-v0.2",
        token=st.secrets["HUGGINGFACE_API_TOKEN"]
    )
except Exception as e:
    # Se a chave não for encontrada ou houver outro erro, exibe um aviso e para a execução.
    st.error("Erro ao conectar com a API do Hugging Face. Verifique sua chave de API nos Secrets.", icon="🔥")
    st.stop()


# --- 2. FUNÇÃO PRINCIPAL DA IA ---

def get_ai_response(historico_conversa):
    """
    Envia o histórico da conversa para a API e retorna a resposta da IA em tempo real (streaming).
    """
    try:
        # Usa o método 'chat_completion' com streaming para uma resposta mais dinâmica.
        response_stream = client.chat_completion(
            messages=historico_conversa,
            max_tokens=2048, # Aumentei para permitir respostas mais elaboradas
            stream=True
        )
        # O 'yield' transforma esta função em um gerador, que é o que o st.write_stream espera.
        for chunk in response_stream:
            pedaco_texto = chunk.choices[0].delta.content
            if pedaco_texto:
                yield pedaco_texto

    except Exception as e:
        # Em caso de erro na chamada da API, informa o usuário.
        yield f"\n\nDesculpe, ocorreu um erro ao processar sua solicitação: {e}"


# --- 3. INICIALIZAÇÃO DO ESTADO DA SESSÃO ---

# O 'st.session_state' é um dicionário que persiste entre as interações do usuário.
# Usamos para "lembrar" o histórico da conversa e o perfil do usuário.

# Inicializa o histórico de mensagens se ainda não existir.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Inicializa o status do perfil do usuário. O app se comporta de forma diferente
# dependendo se o perfil foi preenchido ou não.
if "profile_submitted" not in st.session_state:
    st.session_state.profile_submitted = False


# --- 4. LÓGICA DA INTERFACE (UI) ---

st.title("💡 FinAI: Seu Gestor Financeiro com IA")

# --- SEÇÃO A: QUESTIONÁRIO INICIAL ---
# Esta seção só aparece se o perfil ainda não foi enviado.

if not st.session_state.profile_submitted:
    st.info("👋 Olá! Para começar, preciso entender um pouco sobre seu perfil financeiro.")

    # 'st.form' agrupa vários campos e só envia os dados quando o botão de submit é clicado.
    with st.form("user_profile_form"):
        renda = st.number_input("Qual é a sua renda mensal (R$)?", min_value=0.0, step=100.0)
        objetivo = st.radio(
            "Qual seu principal objetivo financeiro no momento?",
            ("Apenas guardar dinheiro (criar reserva)", "Investir para o futuro")
        )
        # O campo de perfil de investidor só aparece se o usuário escolher "Investir".
        perfil_investidor = "Não se aplica"
        if objetivo == "Investir para o futuro":
            perfil_investidor = st.selectbox(
                "Qual seu perfil de investidor?",
                ("Conservador (prefiro segurança)", "Moderado (busco um equilíbrio)", "Arrojado (busco altos retornos)")
            )
        
        submitted = st.form_submit_button("Começar a Análise!")

        if submitted:
            # Quando o formulário é enviado:
            # 1. Armazena as respostas no estado da sessão.
            st.session_state.user_profile = {
                "renda": renda,
                "objetivo": objetivo,
                "perfil_investidor": perfil_investidor
            }
            # 2. Marca o perfil como enviado para não mostrar o formulário novamente.
            st.session_state.profile_submitted = True

            # 3. Cria o prompt inicial para a IA gerar as 3 estratégias.
            prompt_inicial = f"""
            Você é 'FinAI', um assistente financeiro especialista em finanças pessoais.
            Um usuário com o seguinte perfil acaba de se cadastrar:
            - Renda Mensal: R$ {renda:,.2f}
            - Objetivo Principal: {objetivo}
            - Perfil de Investidor: {perfil_investidor}

            Sua primeira tarefa é gerar três estratégias de economia iniciais, personalizadas e práticas para este usuário.
            Apresente-as em formato de lista numerada. Use uma linguagem encorajadora e comece com uma saudação de boas-vindas.
            """

            # 4. Cria a mensagem de sistema que dará contexto para TODA a conversa futura.
            mensagem_sistema = {
                "role": "system",
                "content": f"""Você é 'FinAI', um assistente financeiro pessoal. Você está conversando com um usuário cujo perfil é: Renda Mensal R${renda:,.2f}, Objetivo: {objetivo}, Perfil: {perfil_investidor}. Sua missão é ajudar o usuário a organizar, analisar e otimizar suas finanças. Responda sempre em português do Brasil, de forma didática e amigável. Baseie suas análises nas informações que o usuário fornecer e no perfil inicial dele."""
            }
            # Adiciona a mensagem de sistema ao histórico (não será exibida, mas usada pela IA).
            st.session_state.messages.append(mensagem_sistema)

            # 5. Adiciona uma mensagem "falsa" do usuário para iniciar a conversa.
            st.session_state.messages.append({"role": "user", "content": prompt_inicial})

            # 6. Força a página a recarregar para passar para a interface de chat.
            st.rerun()

# --- SEÇÃO B: INTERFACE DE CHAT ---
# Esta seção aparece DEPOIS que o perfil é enviado.

if st.session_state.profile_submitted:
    # Exibe todo o histórico de mensagens (exceto a mensagem de sistema).
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Verifica se a última mensagem NÃO foi da IA. Se for o caso, gera uma nova resposta.
    # Isso acontece na primeira vez (para gerar as estratégias) e em cada nova pergunta.
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            # O st.write_stream exibe a resposta da IA em tempo real, palavra por palavra.
            response = st.write_stream(get_ai_response(st.session_state.messages))
        # Adiciona a resposta completa da IA ao histórico.
        st.session_state.messages.append({"role": "assistant", "content": response})

    # 'st.chat_input' cria o campo de texto fixo na parte inferior da tela.
    if prompt := st.chat_input("Digite seus gastos, dúvidas ou peça uma análise..."):
        # Adiciona a nova mensagem do usuário ao histórico.
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Exibe a mensagem do usuário na tela.
        with st.chat_message("user"):
            st.markdown(prompt)

        # Gera e exibe a nova resposta da IA.
        with st.chat_message("assistant"):
            response = st.write_stream(get_ai_response(st.session_state.messages))
        # Adiciona a resposta da IA ao histórico.
        st.session_state.messages.append({"role": "assistant", "content": response})
