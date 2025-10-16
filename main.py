import streamlit as st
from huggingface_hub import InferenceClient

# --- 1. CONFIGURAÇÃO DA PÁGINA E ESTADO INICIAL ---

st.set_page_config(page_title="IA's Conta", page_icon="💡", layout="centered")

# Tenta inicializar o cliente da API do Hugging Face.
try:
    client = InferenceClient(
        model="mistralai/Mistral-7B-Instruct-v0.2",
        token=st.secrets["HUGGINGFACE_API_TOKEN"]
    )
except Exception as e:
    st.error("Erro ao conectar com a API do Hugging Face. Verifique sua chave de API nos Secrets.", icon="🔥")
    st.stop()


# --- 2. FUNÇÃO PRINCIPAL DA IA ---

def get_ai_response(historico_conversa):
    """
    Envia o histórico da conversa para a API e retorna a resposta da IA em tempo real (streaming).
    """
    try:
        response_stream = client.chat_completion(
            messages=historico_conversa,
            max_tokens=2048,
            stream=True
        )
        for chunk in response_stream:
            pedaco_texto = chunk.choices[0].delta.content
            if pedaco_texto:
                yield pedaco_texto

    except Exception as e:
        yield f"\n\nDesculpe, ocorreu um erro ao processar sua solicitação: {e}"


# --- 3. INICIALIZAÇÃO DO ESTADO DA SESSÃO ---

if "messages" not in st.session_state:
    st.session_state.messages = []

if "profile_submitted" not in st.session_state:
    st.session_state.profile_submitted = False


# --- 4. LÓGICA DA INTERFACE (UI) ---

st.title("💡 IA's Conta")
st.markdown("Seu assistente financeiro pessoal, pronto para te ajudar a tomar as melhores decisões.")

# --- SEÇÃO A: QUESTIONÁRIO INICIAL DETALHADO (VERSÃO MELHORADA) ---

if not st.session_state.profile_submitted:
    st.info("👋 Olá! Antes de começarmos, preciso entender seus objetivos para te ajudar da melhor forma.")

    with st.form("user_profile_form"):
        st.subheader("Sobre Você e Seus Objetivos")
        renda = st.number_input("Qual é a sua renda mensal aproximada (R$)?", min_value=0.0, step=100.0, format="%.2f")
        
        objetivos = st.multiselect(
            "Quais são seus principais objetivos financeiros? (Pode marcar mais de um)",
            ["Organizar minhas finanças", "Diminuir meus gastos", "Começar a investir"]
        )

        # Variáveis para as perguntas condicionais
        perfil_investidor = "Não se aplica"
        conhecimento_investimento = "Não se aplica"

        # Se o usuário quer investir, mostramos as perguntas adicionais
        if "Começar a investir" in objetivos:
            st.subheader("Sobre Investimentos")
            
            # Pergunta sobre Nível de Conhecimento (Baixo/Médio/Alto)
            conhecimento_investimento = st.radio(
                "Qual seu nível de conhecimento sobre investimentos?",
                [
                    "Baixo (sou iniciante, prefiro explicações simples)",
                    "Médio (já entendo o básico, como CDB e Ações)",
                    "Alto (tenho experiência e entendo termos técnicos)"
                ],
                help="Isso nos ajuda a adaptar a linguagem para você."
            )
            
            # Pergunta sobre Perfil de Investidor com descrições claras
            perfil_investidor = st.radio(
                "Qual seu perfil de investidor?",
                [
                    "Conservador: Priorizo a segurança do meu dinheiro, mesmo que o retorno seja menor.",
                    "Moderado: Busco um equilíbrio, aceitando um pouco de risco por melhores retornos.",
                    "Arrojado: Meu foco é maximizar os retornos, mesmo que isso signifique correr mais riscos."
                ],
                help="Seu perfil define o tipo de investimento mais adequado para você."
            )
        
        submitted = st.form_submit_button("Gerar meu plano inicial!")

        if submitted:
            if not objetivos:
                st.error("Por favor, selecione pelo menos um objetivo.")
            else:
                # Limpa os dados para enviar à IA (ex: "Baixo" em vez de "Baixo (sou iniciante...)")
                perfil_limpo = perfil_investidor.split(":")[0]
                conhecimento_limpo = conhecimento_investimento.split(" ")[0]

                st.session_state.user_profile = {
                    "renda": renda,
                    "objetivos": ", ".join(objetivos),
                    "perfil_investidor": perfil_limpo,
                    "conhecimento_investimento": conhecimento_limpo
                }
                st.session_state.profile_submitted = True

                prompt_inicial = f"""
                Você é a IA do "IA's Conta", um assistente financeiro especialista.
                Um usuário com o seguinte perfil detalhado acaba de se cadastrar:
                - Renda Mensal: R$ {st.session_state.user_profile['renda']:,.2f}
                - Objetivos: {st.session_state.user_profile['objetivos']}
                - Nível de conhecimento sobre investimentos: {st.session_state.user_profile['conhecimento_investimento']}
                - Perfil de Investidor: {st.session_state.user_profile['perfil_investidor']}

                Sua primeira tarefa é gerar três estratégias iniciais, práticas e altamente personalizadas para este usuário, levando em conta TODOS os seus objetivos.
                Apresente-as em formato de lista numerada. Use uma linguagem encorajadora, didática e comece com uma saudação de boas-vindas.
                """

                mensagem_sistema = {
                    "role": "system",
                    "content": f"""Você é a IA do "IA's Conta", um assistente financeiro pessoal, didático e amigável. Você está conversando com um usuário com este perfil: {st.session_state.user_profile}. Sua missão é ajudá-lo a atingir seus objetivos. Responda sempre em português do Brasil.
                    IMPORTANTE: Adapte sua linguagem ao nível de conhecimento do usuário sobre investimentos ('{st.session_state.user_profile['conhecimento_investimento']}').
                    - Se o nível for 'Baixo', use analogias do dia a dia, evite jargões a todo custo e seja extremamente didático.
                    - Se o nível for 'Médio', pode introduzir conceitos como CDB, Selic, Ações, mas sempre explique-os de forma resumida.
                    - Se o nível for 'Alto', sinta-se à vontade para usar uma linguagem mais técnica e ir direto ao ponto, pois o usuário tem experiência."""
                }
                st.session_state.messages.append(mensagem_sistema)
                st.session_state.messages.append({"role": "user", "content": prompt_inicial})
                st.rerun()

# --- SEÇÃO B: INTERFACE DE CHAT (Permanece a mesma) ---

if st.session_state.profile_submitted:
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            response = st.write_stream(get_ai_response(st.session_state.messages))
        st.session_state.messages.append({"role": "assistant", "content": response})

    if prompt := st.chat_input("Digite seus gastos, dúvidas ou peça uma análise..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = st.write_stream(get_ai_response(st.session_state.messages))
        st.session_state.messages.append({"role": "assistant", "content": response})
