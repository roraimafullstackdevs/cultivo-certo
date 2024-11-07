import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

import streamlit as st
import src.st_chat as st_chat
import src.st_analytics as st_analytics
import src.st_maps as st_maps
import src.st_alerta as st_alerta
import src.st_previsoes as st_previsoes




# Caminho para a logo
logo_path = os.path.join(os.path.dirname(__file__), 'images/icon.png')

st_chat.inicia_memoria()

# Inicializa o estado com a página padrão sendo o Chatbot
if "selected_page" not in st.session_state:
    st.session_state.selected_page = "Chatbot"

# CSS para padronizar o tamanho e a cor dos botões
st.markdown(f"""
    <style>
    .stButton>button {{
        width: 100%;
        margin-bottom: 10px;
        height: 50px;
        border: none;
        border-radius: 5px;
    }}
    .stButton>button[data-baseweb] {{
        background-color: #4CAF50; /* Green */
        color: white;
    }}
    #chatbot_button > button {{
        background-color: {'#45a049' if st.session_state.selected_page == 'Chatbot' else '#4CAF50'};
    }}
    #analytics_button > button {{
        background-color: {'#1E90FF' if st.session_state.selected_page == 'Análise de Dados' else '#008CBA'};
    }}
    #maps_button > button {{
        background-color: {'#FF8C00' if st.session_state.selected_page == 'Mapas' else '#FFA500'};
    }}
    .stButton>button:hover {{
        filter: brightness(85%);
        cursor: pointer;
    }}
    </style>
""", unsafe_allow_html=True)

# st.sidebar.title("Menu")

# Adiciona a logo acima das opções
st.sidebar.image(logo_path, use_column_width=True)

# Lógica dos botões na barra lateral
chatbot_selected = st.sidebar.button("Chatbot", key="chatbot_button")
analytics_selected = st.sidebar.button("Análise de Dados", key="analytics_button")
maps_selected = st.sidebar.button("Mapas", key="maps_button")
alerta_selected = st.sidebar.button("Alertas", key="alerta_button")
previsao_selected = st.sidebar.button("Previsão", key="previsao_button")



# Atualiza o estado da página selecionada
if chatbot_selected:
    st.session_state.selected_page = "Chatbot"
elif analytics_selected:
    st.session_state.selected_page = "Análise de Dados"
elif maps_selected:
    st.session_state.selected_page = "Mapas"
elif alerta_selected:
    st.session_state.selected_page = "Alertas"
elif previsao_selected:
    st.session_state.selected_page = "Previsão"



# Exibe a página selecionada
if st.session_state.selected_page == "Chatbot":
    st_chat.interface()
elif st.session_state.selected_page == "Análise de Dados":
    st_analytics.pagina_analise_dados()
elif st.session_state.selected_page == "Mapas":
    st_maps.pagina_mapas()
elif st.session_state.selected_page == "Alertas":
    st_alerta.pagina_alertas()
elif st.session_state.selected_page == "Previsão":
    st_previsoes.pagina_previsoes()