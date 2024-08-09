import streamlit as st
import pandas as pd

dados = pd.read_csv('dadosbr.csv')

# Funções para filtrar dados
def filtrar_por_profissao_ou_habilidades(dados, palavra_chave):
    return dados[dados[' cargo'].str.contains(palavra_chave, case=False, na=False) | 
                 dados[' habilidades de trabalho'].str.contains(palavra_chave, case=False, na=False)]

def filtrar_por_especialidade(dados, especialidade):
    return dados[dados[' cargo'].str.contains(especialidade, case=False, na=False)]

def filtrar_por_nivel(dados, nivel):
    return dados[dados[' habilidades de trabalho'].str.contains(nivel, case=False, na=False)]

# Função para ordenar dados por relevância
def ordenar_por_relevancia(dados_filtrados, palavra_chave):
    # Preenche NaNs com strings vazias
    dados_filtrados[' cargo'] = dados_filtrados[' cargo'].fillna('')
    dados_filtrados[' habilidades de trabalho'] = dados_filtrados[' habilidades de trabalho'].fillna('')
    
    # Cria colunas de relevância: 2 se a palavra-chave está no título, 1 se está nas habilidades
    dados_filtrados['relevancia'] = dados_filtrados[' cargo'].str.contains(palavra_chave, case=False).astype(int) * 2 + \
                                    dados_filtrados[' habilidades de trabalho'].str.contains(palavra_chave, case=False).astype(int)
    # Ordena por relevância (2 primeiro, depois 1)
    dados_ordenados = dados_filtrados.sort_values(by='relevancia', ascending=False)
    # Remove a coluna de relevância
    dados_ordenados = dados_ordenados.drop(columns=['relevancia'])
    return dados_ordenados

# Define a classe SessionState para armazenar o estado da sessão
class SessionState:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def clear(self):
        self.__dict__.clear()

# Obtém o estado da sessão atual ou cria um novo se não existir
def get_session_state():
    return st.session_state.setdefault('session', SessionState())

st.title('Officium Link')

# Obtém o estado da sessão
session_state = get_session_state()

# Entrada do usuário para profissão ou habilidades
profissao_habilidades = st.text_input("Em qual área você atua ou deseja atuar?", placeholder="Digite a profissão ou habilidades que você possui para começar.")

# Botão de busca por profissão/habilidade
if st.button('Buscar profissão/habilidades'):
    if profissao_habilidades:
        # Filtra os dados com base na profissão ou habilidades
        session_state.dados_filtrados = filtrar_por_profissao_ou_habilidades(dados, profissao_habilidades)
        
        # Verifica se algum resultado foi encontrado
        if session_state.dados_filtrados.empty:
            st.write("Nenhuma correspondência encontrada para a profissão ou habilidades informadas.")
        else:
            # Ordena os dados filtrados por relevância
            session_state.dados_filtrados = ordenar_por_relevancia(session_state.dados_filtrados, profissao_habilidades)
            st.write('''
            :blue[**Encontramos algumas vagas para você!**]''')
            st.write(session_state.dados_filtrados)

# Se houver dados filtrados, exibe os campos de entrada e botões de busca por critério
if hasattr(session_state, 'dados_filtrados'):
    especialidade = st.text_input("Quer encontrar vagas que combinem perfeitamente com suas habilidades? Informe sua especialidade.", placeholder="Digite sua especialidade.")
    if st.button('Buscar por Especialidade'):
        if especialidade:
            # Filtra os dados com base na especialidade
            session_state.dados_filtrados = filtrar_por_especialidade(session_state.dados_filtrados, especialidade)
            if session_state.dados_filtrados.empty:
                st.write("Nenhuma correspondência encontrada para a especialidade informada.")
            else:
                st.write('''
            :blue[**Resultados da busca por especialidade:**]''')
                st.write(session_state.dados_filtrados)

    nivel = st.text_input("Qual é o seu nível de experiência na área?", placeholder="Digite seu nível de experiência (iniciante, intermediário, avançado).")
    if st.button('Buscar por Nível'):
        if nivel:
            # Filtra os dados com base no nível
            session_state.dados_filtrados = filtrar_por_nivel(session_state.dados_filtrados, nivel)
            if session_state.dados_filtrados.empty:
                st.write("Nenhuma correspondência encontrada para o nível informado.")
            else:
                st.write('''
            :blue[**Resultados da busca por nível:**]''')
                st.write(session_state.dados_filtrados)
                
