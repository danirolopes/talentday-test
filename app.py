import streamlit as st
import openai
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_question(previous_questions, previous_answers):
    prompt = f"""
    Você é um entrevistador de IA avaliando candidatos para empreendedorismo em startups.
    Gere uma pergunta múltipla escolha em português, considerando as perguntas e respostas anteriores:
    Perguntas anteriores: {previous_questions}
    Respostas anteriores: {previous_answers}
    
    A pergunta deve ser diferente das anteriores e mais específica.
    Avalie traços como apetite pelo risco, viés de ação, trabalho em ambientes incertos e tomada de decisões com informações limitadas.
    
    Forneça a saída como um JSON com os seguintes campos:
    - pergunta: a pergunta gerada
    - opcoes: lista de 4 opções de resposta
    - explicacao: breve explicação sobre como a pergunta se relaciona com o empreendedorismo
    """

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)

def evaluate_answers(questions, answers):
    prompt = f"""
    Avalie as respostas do candidato para determinar seu potencial como empreendedor de startups.
    Perguntas: {questions}
    Respostas: {answers}
    
    Forneça a saída como um JSON com os seguintes campos:
    - pontuacao: nota de 0 a 10
    - avaliacao: breve avaliação do potencial do candidato como empreendedor
    """

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)

def main():
    st.set_page_config(page_title="Entrevista para Empreendedores", page_icon="🚀", layout="centered")
    st.title("🚀 Avaliação de Potencial Empreendedor")

    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'answers' not in st.session_state:
        st.session_state.answers = []
    if 'current_question' not in st.session_state:
        st.session_state.current_question = None
    if 'evaluation' not in st.session_state:
        st.session_state.evaluation = None

    if len(st.session_state.questions) < 7 and not st.session_state.evaluation:
        if not st.session_state.current_question:
            with st.spinner("Gerando próxima pergunta..."):
                st.session_state.current_question = generate_question(st.session_state.questions, st.session_state.answers)

        st.write(f"### Pergunta {len(st.session_state.questions) + 1}")
        st.write(st.session_state.current_question['pergunta'])
        
        answer = st.radio("Escolha a opção que melhor te descreve:", st.session_state.current_question['opcoes'], key=f"q{len(st.session_state.questions)}")
        
        if st.button("Próxima pergunta"):
            st.session_state.questions.append(st.session_state.current_question['pergunta'])
            st.session_state.answers.append(answer)
            st.session_state.current_question = None
            st.rerun()

    elif not st.session_state.evaluation:
        with st.spinner("Avaliando suas respostas..."):
            st.session_state.evaluation = evaluate_answers(st.session_state.questions, st.session_state.answers)
        st.rerun()

    if st.session_state.evaluation:
        st.write("## Avaliação Final")
        st.write(f"### Pontuação: {st.session_state.evaluation['pontuacao']}/10")
        st.write(st.session_state.evaluation['avaliacao'])

        if st.button("Reiniciar entrevista"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()