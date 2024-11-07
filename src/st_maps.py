
import os
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
from sqlalchemy import create_engine
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Carrega variáveis do .env
load_dotenv()

# Conecta ao banco de dados PostgreSQL usando SQLAlchemy
def get_db_engine():
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_name = os.getenv('DB_NAME')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')

    db_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(db_url)
    return engine

# Função para carregar dados
def load_data(engine):
    with engine.connect() as conn:
        query = "SELECT * FROM dados_coleta"
        df = pd.read_sql_query(query, conn)
    return df

def aplicar_filtros(df):
    st.sidebar.title("Filtros")
    
    st.sidebar.subheader("Filtro de Data")
    
    data_max = datetime.today().date()
    data_min_inicial = data_max - timedelta(days=30)
    data_min = data_max - timedelta(days=60)

    data_inicial, data_final = st.sidebar.date_input(
        "Selecione o intervalo de datas:",
        value=[data_min_inicial, data_max],
        min_value=data_min,
        max_value=data_max,
        key="date_range"
    )
    
    # Filtro de Data
    # data_inicial = st.sidebar.date_input("Data Inicial", df['data_coleta'].min())
    # data_final = st.sidebar.date_input("Data Final", df['data_coleta'].max())

    # Verifique se o intervalo é superior a 30 dias
    if data_final - data_inicial > timedelta(days=30):
        st.sidebar.error("Por favor, selecione um intervalo de no máximo 30 dias")
    else:
        df = df[(df['data_coleta'] >= data_inicial) & (df['data_coleta'] <= data_final)]

    # Filtro de Tipo de Armadilha
    armadilha_opcoes = df['tipo_armadilha'].unique().tolist()
    tipo_armadilha = st.sidebar.multiselect("Tipo de Armadilha", armadilha_opcoes, default=armadilha_opcoes)
    df = df[df['tipo_armadilha'].isin(tipo_armadilha)]

    # Filtro de Tipo de Ambiente
    ambiente_opcoes = df['tipo_ambiente'].unique().tolist()
    tipo_ambiente = st.sidebar.multiselect("Tipo de Ambiente", ambiente_opcoes, default=ambiente_opcoes)
    df = df[df['tipo_ambiente'].isin(tipo_ambiente)]
    
    return df

# Função para a página de mapas
def pagina_mapas():
    st.title("Mapa de Roraima")

    # Conecta ao banco e carrega dados
    engine = get_db_engine()
    df = load_data(engine)

    # Aplica os filtros
    df_filtrado = aplicar_filtros(df)

    # Coordenadas de Roraima
    latitude = 2.737597
    longitude = -62.075099

    # Criação do Mapa com o Folium
    map = folium.Map(location=[latitude, longitude], zoom_start=6)

    # Adição de Marcadores no Mapa
    for idx, row in df_filtrado.iterrows():
        popup_text = (
            f"Cidade: {row['cidade']}<br>"
            f"Técnico: {row['tecnico']}<br>"
            f"Tipo de Armadilha: {row['tipo_armadilha']}<br>"
            f"Total Captura: {row['total_captura']}<br>"
            f"Ação Tomada: {row['acao_tomada']}<br>"
            f"Data de Coleta: {row['data_coleta']}<br>"
            f"Hora de Coleta: {row['hora_coleta']}<br>"
            f"Temp. Média Últimos Dias: {row['temp_media_ultimos_dias']}<br>"
            f"Temp. Máx. Último Dias: {row['temp_max_ultimo_dias']}<br>"
            f"Temp. Mín. Últimos Dias: {row['temp_min_ultimos_dias']}<br>"
            f"Precipitação Acumulada: {row['precipitacao_acumulada']}<br>"
            f"Tipo de Isca: {row['tipo_de_isca']}<br>"
            f"Tempo Exposição Armadilha: {row['tempo_exposição_armadilha']}<br>"
            f"Tipo de Ambiente: {row['tipo_ambiente']}<br>"
            f"Proximidade Árvores Frutíferas: {row['proximidade_arvores_frutiferas']}<br>"
            f"Latitude: {row['latitude']}<br>"
            f"Longitude: {row['longitude']}<br>"
            f"Hospedeiros: {row['hospedeiros']}"
        )
        folium.Marker(
            [row['latitude'], row['longitude']],
            popup=popup_text,
            icon=folium.Icon(color='blue')
        ).add_to(map)

    # Renderiza o Mapa com Folium
    folium_static(map)