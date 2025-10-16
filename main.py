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

# --- 2. FUNÇÃO PRINCIPAL DA IA (COM FILTRO) ---

def get_ai_response(historico_conversa):
    """Envia o histórico para a API e retorna a resposta da IA em tempo real."""
    try:
        response_stream = client.chat_completion(
            messages=historico_conversa, max_tokens=2048, stream=True
        )
        for chunk in response_stream:
            pedaco_texto = chunk.choices[0].delta.content
            # --- MELHORIA 1: FILTRO DE TOKENS ESPECIAIS ---
            # Se o pedaço de texto existir E não for o token de fim de sequência, nós o exibimos.
            if pedaco_texto and "</s>" not in pedaco_texto:
                yield pedaco_texto
    except Exception as e:
        yield f"\n\nDesculpe, ocorreu um erro ao processar sua solicitação: {e}"

# --- 3. INICIALIZAÇÃO DO ESTADO DA SESSÃO ---

if "step" not in st.session_state:
    st.session_state.step = 1
if "form_data" not in st.session_state:
    st.session_state.form_data = {}
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. LÓGICA DA INTERFACE (UI) ---

st.title("💡 IA's Conta")
st.markdown("Seu assistente financeiro pessoal, pronto para te ajudar a tomar as melhores decisões.")

# --- SEÇÃO A: QUESTIONÁRIO INICIAL EM PASSOS (sem alterações aqui) ---
if st.session_state.step == 1:
    st.info("👋 Olá! Vamos começar definindo seu perfil e objetivos.")
    with st.form("step1_form"):
        renda = st.number_input("Qual é a sua renda mensal aproximada (R$)?", min_value=0.0, step=100.0, format="%.2f")
        objetivos = st.multiselect(
            "Quais são seus principais objetivos financeiros? (Pode marcar mais de um)",
            ["Organizar minhas finanças", "Diminuir meus gastos", "Começar a investir"]
        )
        submitted_step1 = st.form_submit_button("Próximo")
        if submitted_step1:
            if not objetivos:
                st.error("Por favor, selecione pelo menos um objetivo para continuar.")
            else:
                st.session_state.form_data['renda'] = renda
                st.session_state.form_data['objetivos'] = objetivos
                if "Começar a investir" not in objetivos:
                    st.session_state.step = "final"
                else:
                    st.session_state.step = 2
                st.rerun()

if st.session_state.step == 2:
    st.info("Ótimo! Agora, vamos entender melhor seu perfil para investimentos.")
    with st.form("step2_form"):
        conhecimento_investimento = st.radio(
            "Qual seu nível de conhecimento sobre investimentos?",
            ["Baixo (sou iniciante, prefiro explicações simples)", "Médio (já entendo o básico, como CDB e Ações)", "Alto (tenho experiência e entendo termos técnicos)"],
            help="Isso nos ajuda a adaptar a linguagem para você."
        )
        perfil_investidor = st.radio(
            "Qual seu perfil de investidor?",
            ["Conservador: Priorizo a segurança do meu dinheiro, mesmo que o retorno seja menor.", "Moderado: Busco um equilíbrio, aceitando um pouco de risco por melhores retornos.", "Arrojado: Meu foco é maximizar os retornos, mesmo que isso signifique correr mais riscos."],
            help="Seu perfil define o tipo de investimento mais adequado para você."
        )
        submitted_step2 = st.form_submit_button("Gerar meu plano inicial!")
        if submitted_step2:
            st.session_state.form_data['conhecimento_investimento'] = conhecimento_investimento
            st.session_state.form_data['perfil_investidor'] = perfil_investidor
            st.session_state.step = "final"
            st.rerun()

# PASSO FINAL: Montar o prompt e iniciar o chat
if st.session_state.step == "final" and not st.session_state.messages:
    data = st.session_state.form_data
    perfil_limpo = data.get('perfil_investidor', 'Não se aplica').split(':')[0]
    conhecimento_limpo = data.get('conhecimento_investimento', 'Não se aplica').split(' ')[0]

    st.session_state.user_profile = {
        "renda": data['renda'], "objetivos": ", ".join(data['objetivos']),
        "perfil_investidor": perfil_limpo, "conhecimento_investimento": conhecimento_limpo
    }

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

    # --- MELHORIA 2: INSTRUÇÕES DE SISTEMA MAIS DETALHADAS ---
    mensagem_sistema = {
        "role": "system",
        "content": f"""Você é a IA do "IA's Conta", um assistente financeiro pessoal. Sua personalidade é didática, paciente e confiável. Você está conversando com um usuário com este perfil: {st.session_state.user_profile}.
        REGRAS PRINCIPAIS:
        1.  **IDIOMA:** Responda TUDO exclusivamente em português do Brasil. Revise suas respostas para garantir que não haja palavras em inglês.
        2.  **TOM DE VOZ:** Use uma linguagem natural e conversacional, como um verdadeiro consultor financeiro faria. Evite ser robótico.
        3.  **ADAPTAÇÃO:** Adapte sua linguagem ao nível de conhecimento do usuário sobre investimentos ('{st.session_state.user_profile['conhecimento_investimento']}').
            - Se 'Baixo': Use analogias do dia a dia, evite jargões a todo custo e seja extremamente didático.
            - Se 'Médio': Pode introduzir conceitos como CDB, Selic, Ações, mas sempre explique-os de forma resumida.
            - Se 'Alto': Sinta-se à vontade para usar uma linguagem mais técnica e ir direto ao ponto.
        4.  **SEGURANÇA:** Sempre inclua um aviso de que suas sugestões não são recomendações de investimento formais e que o usuário deve consultar um profissional certificado quando for tomar decisões de alto risco.
        """
    }
    st.session_state.messages.append(mensagem_sistema)
    st.session_state.messages.append({"role": "user", "content": prompt_inicial})
    st.rerun()

# --- SEÇÃO B: INTERFACE DE CHAT ---

if st.session_state.step == "final":
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
